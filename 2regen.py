import streamlit as st
import json
import re
import time
from abc_response import abc_response  # Import your LLM function

# Set page configuration
st.set_page_config(
    page_title="ReAct Agent",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS for better UI
st.markdown("""
<style>
.chat-message {
    padding: 1.5rem; 
    border-radius: 0.5rem; 
    margin-bottom: 1rem;
    display: flex;
    flex-direction: row;
    align-items: flex-start;
}
.chat-message.user {
    background-color: #f0f2f6;
}
.chat-message.assistant, .chat-message.tool, .chat-message.plan {
    background-color: #e6f7ff;
}
.chat-message.plan {
    background-color: #fff3e0;
    border-left: 4px solid #ff9800;
}
.chat-message.tool {
    background-color: #e8f5e9;
    border-left: 4px solid #4caf50;
}
.avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    object-fit: cover;
    margin-right: 1rem;
}
.message-content {
    flex: 1;
}
.thinking {
    color: #888;
    font-style: italic;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0% { opacity: 0.6; }
    50% { opacity: 1; }
    100% { opacity: 0.6; }
}
.step-counter {
    background-color: #ff5722;
    color: white;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-right: 8px;
    font-size: 14px;
}
.tools-header {
    font-weight: bold;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    color: #333;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thinking" not in st.session_state:
    st.session_state.thinking = False
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "max_steps" not in st.session_state:
    st.session_state.max_steps = 10
if "current_plan" not in st.session_state:
    st.session_state.current_plan = []
if "execution_started" not in st.session_state:
    st.session_state.execution_started = False

# Tool functions
def calculator_tool(expression):
    """Evaluates a mathematical expression."""
    try:
        # Safely evaluate the expression
        result = eval(expression, {"__builtins__": {}}, {"abs": abs, "round": round, "max": max, "min": min})
        return f"Calculator result: {result}"
    except Exception as e:
        return f"Calculator error: {str(e)}"

# Display header
st.title("🤖 ReAct Agent")
st.markdown("I'll help with your tasks by making a plan and executing it step by step.")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.max_steps = st.slider("Max steps per query", 3, 15, 10)
    
    st.markdown("### Available Tools")
    st.markdown("- 🧮 **Calculator**: Perform math calculations")
    st.markdown("- 💬 **Conversation**: Ask for clarification or follow-up")
    
    st.markdown("---")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.current_step = 0
        st.session_state.current_plan = []
        st.session_state.execution_started = False
        st.rerun()

# Function to parse the LLM output
def parse_llm_response(response):
    """Parse the response from the LLM to extract action and action input."""
    try:
        # Try to parse as JSON directly
        if response.startswith("{") and response.endswith("}"):
            try:
                parsed = json.loads(response)
                return parsed
            except json.JSONDecodeError:
                pass
        
        # Regular expression patterns
        action_pattern = r"Action: *(.*?)[\n$]"
        action_input_pattern = r"Action Input: *(.*?)(?:\n|$)"
        thought_pattern = r"Thought: *(.*?)(?:\n|$)"
        finish_pattern = r"(FINISH|finish)"
        
        # Extract components
        action_match = re.search(action_pattern, response, re.DOTALL)
        action_input_match = re.search(action_input_pattern, response, re.DOTALL)
        thought_match = re.search(thought_pattern, response, re.DOTALL)
        finish_match = re.search(finish_pattern, response)
        
        action = action_match.group(1).strip() if action_match else None
        action_input = action_input_match.group(1).strip() if action_input_match else None
        thought = thought_match.group(1).strip() if thought_match else None
        
        # Check if finished
        if finish_match:
            return {"action": "FINISH", "action_input": thought or "Task completed."}
        
        return {
            "thought": thought,
            "action": action,
            "action_input": action_input
        }
    except Exception as e:
        return {"error": f"Failed to parse LLM response: {str(e)}", "raw_response": response}

# Function to generate the prompt for the LLM
def generate_prompt(user_query, conversation_history, step_count):
    prompt = f"""You are a ReAct (Reasoning and Acting) agent that solves tasks step by step.
    
AVAILABLE TOOLS:
1. Calculator: Use for math calculations. Format: Action: Calculator, Action Input: [expression]
2. Conversation: Use to respond to the user, ask clarifying questions, or provide information. Format: Action: Conversation, Action Input: [your message]

TASK: {user_query}

FORMAT YOUR RESPONSE:
Thought: [your reasoning about the current step]
Action: [one of: Calculator, Conversation, FINISH]
Action Input: [input for the action]

You are on step {step_count} of a max {st.session_state.max_steps} steps. Be efficient with your steps.
Always use the specified format to ensure I can parse your response.
When the task is complete, use "Action: FINISH" to end the process.

Previous conversation:
"""
    
    for message in conversation_history:
        if message["role"] == "user":
            prompt += f"\nUser: {message['content']}\n"
        elif message["role"] == "assistant":
            prompt += f"\nAssistant: {message['content']}\n"
        elif message["role"] == "tool":
            prompt += f"\nTool ({message['tool']}): {message['content']}\n"
        elif message["role"] == "plan":
            prompt += f"\nPlan: {message['content']}\n"
    
    return prompt

# Function to generate a plan
def generate_plan(user_query):
    plan_prompt = f"""You are a planning assistant. Given a user query, create a step-by-step plan to solve it.
    
AVAILABLE TOOLS:
1. Calculator: Use for math calculations
2. Conversation: Use to respond to the user, ask clarifying questions, or provide information

USER QUERY: {user_query}

Create a concise, numbered plan with 2-5 steps total. Don't execute the steps, just plan them.
FORMAT: Return a numbered list of steps, with each step on a new line.
"""
    
    try:
        plan_response = abc_response(plan_prompt)
        # Extract just the numbered list from the response
        plan_steps = re.findall(r'\d+\.\s*(.*?)(?:\n|$)', plan_response, re.DOTALL)
        return plan_steps
    except Exception as e:
        return [f"Error generating plan: {str(e)}", "Proceeding with direct execution"]

# Function to display chat messages
def display_message(role, content, tool=None, step=None):
    with st.chat_message(role):
        if step is not None:
            st.markdown(f'<div class="step-counter">{step}</div> {content}', unsafe_allow_html=True)
        else:
            st.write(content)

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "tool":
        display_message("assistant", f"🛠️ **Tool ({message['tool']})**: {message['content']}")
    elif message["role"] == "plan":
        plan_html = "<div class='chat-message plan'><strong>📋 Plan:</strong><ol>"
        for step in message["content"]:
            plan_html += f"<li>{step}</li>"
        plan_html += "</ol></div>"
        st.markdown(plan_html, unsafe_allow_html=True)
    else:
        display_message(message["role"], message["content"])

# User input
user_query = st.chat_input("What can I help you with today?")

# Process user query
if user_query:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})
    display_message("user", user_query)
    
    # Reset execution state for new query
    st.session_state.current_step = 0
    st.session_state.execution_started = False
    st.session_state.current_plan = []
    
    # Show thinking indicator
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown("<div class='thinking'>Thinking...</div>", unsafe_allow_html=True)
    
    # Generate plan
    plan_steps = generate_plan(user_query)
    st.session_state.current_plan = plan_steps
    
    # Add plan to chat history
    st.session_state.messages.append({"role": "plan", "content": plan_steps})
    
    # Display plan
    plan_html = "<div class='chat-message plan'><strong>📋 Plan:</strong><ol>"
    for step in plan_steps:
        plan_html += f"<li>{step}</li>"
    plan_html += "</ol></div>"
    thinking_placeholder.markdown(plan_html, unsafe_allow_html=True)
    
    # Set execution flag
    st.session_state.execution_started = True
    st.experimental_rerun()

# Execute plan if needed
if st.session_state.execution_started and st.session_state.current_step < st.session_state.max_steps:
    # Show thinking indicator for execution
    execution_placeholder = st.empty()
    execution_placeholder.markdown(f"<div class='thinking'>Executing step {st.session_state.current_step + 1}...</div>", unsafe_allow_html=True)
    
    # Generate prompt and get LLM response
    prompt = generate_prompt(
        user_query=st.session_state.messages[0]["content"] if len(st.session_state.messages) > 0 else "",
        conversation_history=st.session_state.messages,
        step_count=st.session_state.current_step + 1
    )
    
    try:
        # Call LLM
        response = abc_response(prompt)
        
        # Parse response
        parsed_response = parse_llm_response(response)
        
        # Handle error in parsing
        if "error" in parsed_response:
            st.error(f"Error: {parsed_response['error']}")
            st.code(parsed_response["raw_response"])
            st.session_state.execution_started = False
        else:
            # Process the action
            action = parsed_response.get("action")
            action_input = parsed_response.get("action_input")
            thought = parsed_response.get("thought", "")
            
            # Display thought
            if thought:
                display_message("assistant", f"💭 **Thought**: {thought}", step=st.session_state.current_step + 1)
                st.session_state.messages.append({"role": "assistant", "content": f"💭 Thought: {thought}"})
            
            # Handle different actions
            if action == "Calculator":
                # Execute calculator
                result = calculator_tool(action_input)
                display_message("assistant", f"🛠️ **Calculator**: {action_input}", step=st.session_state.current_step + 1)
                display_message("assistant", result)
                st.session_state.messages.append({"role": "tool", "tool": "Calculator", "content": result})
            
            elif action == "Conversation":
                # Display conversation response
                display_message("assistant", action_input, step=st.session_state.current_step + 1)
                st.session_state.messages.append({"role": "assistant", "content": action_input})
            
            elif action == "FINISH":
                # Display final response
                display_message("assistant", f"✅ **Final Answer**: {action_input}", step=st.session_state.current_step + 1)
                st.session_state.messages.append({"role": "assistant", "content": f"✅ Final Answer: {action_input}"})
                st.session_state.execution_started = False
            
            # Increment step counter
            st.session_state.current_step += 1
            
            # Check if max steps reached
            if st.session_state.current_step >= st.session_state.max_steps:
                display_message("assistant", "⚠️ Maximum number of steps reached. I'll stop here.")
                st.session_state.messages.append({"role": "assistant", "content": "⚠️ Maximum number of steps reached."})
                st.session_state.execution_started = False
            
            # Clear thinking indicator
            execution_placeholder.empty()
            
            # Rerun if still executing
            if st.session_state.execution_started:
                time.sleep(0.5)  # Small delay for better UX
                st.experimental_rerun()
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.session_state.execution_started = False
        execution_placeholder.empty()
