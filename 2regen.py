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
.chat-message.assistant {
    background-color: #e6f7ff;
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
.expandable-section {
    border: 1px solid #ddd;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    overflow: hidden;
}
.expandable-header {
    background-color: #f7f7f7;
    padding: 0.75rem 1rem;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: bold;
}
.expandable-content {
    padding: 1rem;
    border-top: 1px solid #ddd;
    background-color: #fff;
}
.plan-item {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
}
.plan-item.completed {
    color: #4caf50;
}
.plan-item.active {
    color: #2196f3;
    font-weight: bold;
}
.step-indicator {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background-color: #e0e0e0;
    color: #333;
    margin-right: 0.75rem;
    font-size: 12px;
}
.step-indicator.completed {
    background-color: #4caf50;
    color: white;
}
.step-indicator.active {
    background-color: #2196f3;
    color: white;
}
.agent-header {
    background-color: #e53935;
    color: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin-bottom: 1.5rem;
}
.agent-capabilities {
    margin-top: 1rem;
}
.agent-capabilities ul {
    padding-left: 1.5rem;
}
.card {
    border: 1px solid #ddd;
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 1rem;
    background-color: white;
}
.thought-process {
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 1rem;
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
if "show_thought_process" not in st.session_state:
    st.session_state.show_thought_process = False
if "show_plan" not in st.session_state:
    st.session_state.show_plan = False
if "first_time" not in st.session_state:
    st.session_state.first_time = True
if "thoughts" not in st.session_state:
    st.session_state.thoughts = []

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
if st.session_state.first_time:
    st.markdown("""
    <div class="agent-header">
        <h1>Hello! I am a React Agent specialized in helping with various tasks. How can I assist you today?</h1>
        <div class="agent-capabilities">
            <ul>
                <li>Run calculations</li>
                <li>Run small Python code</li>
                <li>File uploads (CSV/JSON) for preview</li>
            </ul>
        </div>
        <p>You can also upload a file using the [+] button.</p>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.first_time = False

# Sidebar for settings and information
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.markdown("### Available Tools")
    st.markdown("- 🧮 **Calculator**: Perform math calculations")
    st.markdown("- 💬 **Conversation**: Ask for clarification or follow-up")
    
    st.markdown("---")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.current_step = 0
        st.session_state.current_plan = []
        st.session_state.execution_started = False
        st.session_state.thoughts = []
        st.session_state.first_time = True
        st.rerun()

# Function to parse the LLM output
def parse_llm_response(response):
    """Parse the response from the LLM to extract action and action input."""
    try:
        # Find any JSON object in the response
        json_match = re.search(r'({.*})', response, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                # Check if this is a valid format with our expected keys
                if "action" in parsed and "action_input" in parsed:
                    return parsed
            except json.JSONDecodeError:
                pass
                
        # Regular expression patterns for fallback
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
        if finish_match or (action and action.upper() == "FINISH"):
            return {"action": "FINISH", "action_input": action_input or thought or "Task completed."}
        
        return {
            "thought": thought,
            "action": action,
            "action_input": action_input
        }
    except Exception as e:
        return {"error": f"Failed to parse LLM response: {str(e)}", "raw_response": response}

# Function to generate the prompt for the LLM
def generate_prompt(user_query, conversation_history, step_count, plan):
    prompt = f"""You are a ReAct (Reasoning and Acting) agent that solves tasks step by step.
    
AVAILABLE TOOLS:
1. Calculator: Use for math calculations. Format: Action: Calculator, Action Input: [expression]
2. Conversation: Use to respond to the user, ask clarifying questions, or provide information. Format: Action: Conversation, Action Input: [your message]

TASK: {user_query}

RESPONSE FORMAT:
You must return a valid JSON object with the following structure:
{{
  "thought": "your reasoning about what to do next",
  "action": "Calculator or Conversation or FINISH",
  "action_input": "input for the action"
}}

You are on step {step_count} of a max {st.session_state.max_steps} steps. {st.session_state.max_steps - step_count} steps remain.
Your goal is to complete the task in as few steps as possible. Be concise but thorough.
The final step in your plan must be a FINISH step that provides the final answer.

CURRENT PLAN:
"""
    
    # Add the plan to the prompt
    for i, step in enumerate(plan):
        status = "COMPLETED" if i < step_count - 1 else "CURRENT" if i == step_count - 1 else "PENDING"
        prompt += f"{i+1}. {step} [{status}]\n"
    
    # Get the last step result if there is one
    last_step_result = None
    if step_count > 1 and len(conversation_history) >= 2:
        # Look for the most recent tool or assistant message
        for message in reversed(conversation_history):
            if message["role"] in ["tool", "assistant"] and message.get("thought") != True:
                last_step_result = message["content"]
                if message["role"] == "tool":
                    last_step_result = f"Tool ({message.get('tool', 'unknown')}): {last_step_result}"
                break
    
    # Only include latest context
    prompt += "\nCONTEXT:\n"
    prompt += f"User Query: {user_query}\n"
    
    if last_step_result:
        prompt += f"Last Step Result: {last_step_result}\n"
    
    prompt += f"\nCurrent Step ({step_count}): {plan[step_count-1] if step_count-1 < len(plan) else 'Complete the task'}\n"
    
    if step_count < len(plan):
        prompt += f"Next Step ({step_count+1}): {plan[step_count]}\n"
    
    return prompt

# Function to generate a plan
def generate_plan(user_query):
    plan_prompt = f"""You are a planning assistant. Given a user query, create a step-by-step plan to solve it.
    
AVAILABLE TOOLS:
1. Calculator: Use for math calculations
2. Conversation: Use to respond to the user, ask clarifying questions, or provide information
3. FINISH: Complete the task and provide final answer

USER QUERY: {user_query}

Create a concise, efficient, step-by-step plan with 2-5 steps total. Don't execute the steps, just plan them.
Focus on solving the query in as few steps as possible. Each step should be a clear action.

IMPORTANT REQUIREMENTS:
1. The final step MUST ALWAYS be "FINISH: Provide the final answer to the user"
2. Use as few steps as possible while still solving the problem correctly
3. Be specific about what each step will accomplish
4. The final FINISH step is mandatory for task completion

FORMAT: Return a numbered list of steps, with each step on a new line.
"""
    
    try:
        plan_response = abc_response(plan_prompt)
        # Extract just the numbered list from the response
        plan_steps = re.findall(r'\d+\.\s*(.*?)(?:\n|$)', plan_response, re.DOTALL)
        
        # Make sure the last step is about providing the final answer with FINISH
        if plan_steps:
            # Check if the last step mentions FINISH
            if not any("FINISH" in step.upper() for step in plan_steps):
                # If the last step mentions final answer but not FINISH, update it
                if "final answer" in plan_steps[-1].lower():
                    plan_steps[-1] = "FINISH: " + plan_steps[-1]
                else:
                    # Otherwise add a new FINISH step
                    plan_steps.append("FINISH: Provide the final answer to the user")
            
        return plan_steps
    except Exception as e:
        return [f"Error generating plan: {str(e)}", "Proceeding with direct execution", "FINISH: Provide the final answer to the user"]

# Function to display chat messages
def display_message(role, content):
    with st.chat_message(role):
        st.write(content)

# Expandable section component
def expandable_section(header, content, key, default_open=False):
    with st.expander(header, expanded=default_open):
        st.markdown(content)

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user" or (message["role"] == "assistant" and "thought" not in message and "tool" not in message):
        display_message(message["role"], message["content"])

# Display thought process expandable section if there are thoughts
if st.session_state.thoughts and not st.session_state.thinking:
    with st.expander("Thought Process", expanded=False):
        for i, thought in enumerate(st.session_state.thoughts):
            st.markdown(f"### Step {i+1}")
            st.markdown(f"**Thought:** {thought}")

# Display plan expandable section if there is a plan
if st.session_state.current_plan and not st.session_state.thinking:
    with st.expander("Plan", expanded=False):
        for i, step in enumerate(st.session_state.current_plan):
            status = "completed" if i < st.session_state.current_step else "active" if i == st.session_state.current_step else ""
            st.markdown(
                f"""<div class="plan-item {status}">
                    <div class="step-indicator {status}">{i+1}</div>
                    {step}
                </div>""", 
                unsafe_allow_html=True
            )

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
    st.session_state.thoughts = []
    
    # Show thinking indicator
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown("<div class='thinking'>Agent is typing...</div>", unsafe_allow_html=True)
    
    # Generate plan
    plan_steps = generate_plan(user_query)
    st.session_state.current_plan = plan_steps
    
    # Set execution flag
    st.session_state.execution_started = True
    st.rerun()

# Execute plan if needed
if st.session_state.execution_started and st.session_state.current_step < st.session_state.max_steps:
    # Show thinking indicator for execution
    execution_placeholder = st.empty()
    if st.session_state.current_step == 0:
        execution_placeholder.markdown("<div class='thinking'>Agent is typing...</div>", unsafe_allow_html=True)
    else:
        execution_placeholder.markdown(f"<div class='thinking'>Executing step {st.session_state.current_step + 1}...</div>", unsafe_allow_html=True)
    
    # Generate prompt and get LLM response
    prompt = generate_prompt(
        user_query=st.session_state.messages[0]["content"] if len(st.session_state.messages) > 0 else "",
        conversation_history=st.session_state.messages,
        step_count=st.session_state.current_step + 1,
        plan=st.session_state.current_plan
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
            
            # Store thought
            if thought:
                st.session_state.thoughts.append(thought)
            
            # Handle different actions
            if action == "Calculator":
                # Execute calculator
                result = calculator_tool(action_input)
                st.session_state.messages.append({"role": "tool", "tool": "Calculator", "content": result})
            
            elif action == "Conversation":
                # Display conversation response
                display_message("assistant", action_input)
                st.session_state.messages.append({"role": "assistant", "content": action_input})
            
            elif action == "FINISH":
                # Display final response
                display_message("assistant", action_input)
                st.session_state.messages.append({"role": "assistant", "content": action_input})
                st.session_state.execution_started = False
            
            # Increment step counter
            st.session_state.current_step += 1
            
            # Check if max steps reached
            if st.session_state.current_step >= st.session_state.max_steps:
                display_message("assistant", "I've reached the maximum number of steps. Here's what I know so far.")
                st.session_state.messages.append({"role": "assistant", "content": "I've reached the maximum number of steps. Here's what I know so far."})
                st.session_state.execution_started = False
            
            # Clear thinking indicator
            execution_placeholder.empty()
            
            # Rerun if still executing
            if st.session_state.execution_started:
                time.sleep(0.5)  # Small delay for better UX
                st.rerun()
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.session_state.execution_started = False
        execution_placeholder.empty()
