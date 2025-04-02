import streamlit as st
import json
import re
import time
from abc_response import abc_response  # Import your LLM function

# Set page configuration
st.set_page_config(
    page_title="ReAct Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for professional chat UI
st.markdown("""
<style>
/* Global styles */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f9f9f9;
}

.main {
    background-color: #f9f9f9;
    max-width: 1200px;
    margin: 0 auto;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 0rem;
}

/* Header styles */
h1 {
    color: #1e3a8a;
    font-weight: 600;
    text-align: center;
    margin-bottom: 0.5rem;
}

.subtitle {
    text-align: center;
    color: #6b7280;
    margin-bottom: 2rem;
}

/* Chat container */
.chat-container {
    max-width: 850px;
    margin: 0 auto;
    padding: 1rem;
    border-radius: 0.75rem;
    background-color: #ffffff;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    height: calc(100vh - 200px);
    display: flex;
    flex-direction: column;
}

.messages-container {
    flex: 1;
    overflow-y: auto;
    padding-right: 0.5rem;
    margin-bottom: 1rem;
}

/* Message bubbles */
.message {
    display: flex;
    margin-bottom: 1rem;
}

.message.user {
    justify-content: flex-end;
}

.message.assistant {
    justify-content: flex-start;
}

.message-bubble {
    padding: 0.75rem 1rem;
    border-radius: 1rem;
    max-width: 80%;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.user .message-bubble {
    background-color: #3b82f6;
    color: white;
    border-top-right-radius: 0.25rem;
}

.assistant .message-bubble {
    background-color: #f3f4f6;
    color: #1f2937;
    border-top-left-radius: 0.25rem;
}

/* Plan collapsible */
.plan-container {
    margin: 1rem 0;
    border-radius: 0.5rem;
    background-color: #fffbeb;
    border: 1px solid #fbbf24;
    overflow: hidden;
}

.plan-header {
    padding: 0.75rem 1rem;
    background-color: #fef3c7;
    font-weight: 500;
    color: #92400e;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.plan-content {
    padding: 1rem;
    display: none;
}

.plan-steps {
    margin-left: 1.5rem;
    margin-bottom: 0;
}

/* Tool output */
.tool-output {
    margin: 0.5rem 0 0.5rem 2.5rem;
    padding: 0.75rem 1rem;
    background-color: #ecfdf5;
    border-left: 3px solid #059669;
    border-radius: 0.25rem;
    font-family: 'Courier New', monospace;
    font-size: 0.875rem;
}

/* Code formatting */
.code-block {
    background-color: #1e1e1e;
    color: #d4d4d4;
    padding: 1rem;
    border-radius: 0.5rem;
    font-family: 'Courier New', Courier, monospace;
    position: relative;
    margin: 1rem 0;
    overflow-x: auto;
}

.copy-button {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.25rem;
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    cursor: pointer;
}

/* Input area */
.input-container {
    display: flex;
    margin-top: auto;
    padding-top: 1rem;
    border-top: 1px solid #e5e7eb;
}

.stTextInput input {
    border-radius: 1.5rem;
    border: 1px solid #d1d5db;
    padding: 0.75rem 1rem;
    width: 100%;
    font-size: 1rem;
}

.stTextInput input:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

/* Thinking animation */
.thinking {
    padding: 0.5rem 1rem;
    margin-left: 2.5rem;
    background-color: #f3f4f6;
    border-radius: 1rem;
    color: #6b7280;
    font-style: italic;
    display: inline-flex;
    align-items: center;
    max-width: 80%;
}

.thinking::after {
    content: '';
    width: 1rem;
    height: 1rem;
    margin-left: 0.5rem;
    background-image: radial-gradient(circle, #3b82f6 3px, transparent 3px);
    background-size: 0.5rem 0.5rem;
    animation: thinking 1s infinite;
}

@keyframes thinking {
    0% { opacity: 0.2; }
    20% { opacity: 1; }
    100% { opacity: 0.2; }
}

/* Syntax highlighting */
.python-code {
    background-color: #1e1e1e;
    color: #d4d4d4;
}
.python-keyword { color: #569cd6; }
.python-string { color: #ce9178; }
.python-comment { color: #6a9955; }
.python-function { color: #dcdcaa; }
.python-class { color: #4ec9b0; }
.python-number { color: #b5cea8; }

/* Sidebar */
.css-1544g2n {
    padding-top: 2rem;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {
    visibility: hidden;
}

/* Enhance readability of markdown */
.markdown-text-container {
    line-height: 1.6;
}

/* Final answer formatting */
.final-answer {
    background-color: #f0f9ff;
    border-left: 3px solid #3b82f6;
    padding: 0.75rem 1rem;
    margin-top: 0.5rem;
    border-radius: 0.25rem;
}

/* Step indicator */
.step-indicator {
    font-size: 0.75rem;
    color: #6b7280;
    margin-bottom: 0.25rem;
    display: block;
}

/* For JavaScript interaction */
.st-emotion-cache-s1k4sy {
    margin-top: 0 !important;
}

.st-emotion-cache-16txtl3 {
    padding: 0 !important;
}

.stButton button {
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 1.5rem;
    padding: 0.5rem 1.5rem;
    font-weight: 500;
}

.stButton button:hover {
    background-color: #2563eb;
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Toggle plan visibility
    const planHeader = document.querySelector('.plan-header');
    const planContent = document.querySelector('.plan-content');
    
    if (planHeader && planContent) {
        planHeader.addEventListener('click', function() {
            if (planContent.style.display === 'none' || !planContent.style.display) {
                planContent.style.display = 'block';
                this.querySelector('.expand-icon').textContent = '-';
            } else {
                planContent.style.display = 'none';
                this.querySelector('.expand-icon').textContent = '+';
            }
        });
    }
});
</script>
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
if "final_answers" not in st.session_state:
    st.session_state.final_answers = []
if "user_queries" not in st.session_state:
    st.session_state.user_queries = []
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# Tool functions
def calculator_tool(expression):
    """Evaluates a mathematical expression."""
    try:
        # Create a safe environment for evaluation
        safe_dict = {
            "abs": abs, "round": round, "max": max, "min": min,
            "sum": sum, "len": len, "pow": pow, "int": int, "float": float
        }
        
        # Safely evaluate the expression
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

# Function to format code with syntax highlighting
def format_code_block(code, language="python"):
    # Simple syntax highlighting for Python
    if language == "python":
        # Replace Python keywords with styled spans
        keywords = ["import", "from", "def", "class", "if", "else", "elif", "for", "while", 
                   "try", "except", "return", "with", "as", "in", "not", "and", "or", "True", "False", "None"]
        
        for keyword in keywords:
            pattern = r'\b' + keyword + r'\b'
            code = re.sub(pattern, f'<span class="python-keyword">{keyword}</span>', code)
        
        # Highlight strings
        code = re.sub(r'("[^"]*")', r'<span class="python-string">\1</span>', code)
        code = re.sub(r"('[^']*')", r'<span class="python-string">\1</span>', code)
        
        # Highlight comments
        code = re.sub(r'(#.*)$', r'<span class="python-comment">\1</span>', code, flags=re.MULTILINE)
        
        # Highlight function calls
        code = re.sub(r'\b(\w+)\(', r'<span class="python-function">\1</span>(', code)
        
        # Highlight numbers
        code = re.sub(r'\b(\d+)\b', r'<span class="python-number">\1</span>', code)
    
    # Create HTML structure for code block with copy button
    copy_button = f'''
    <button class="copy-button" onclick="
        const code = this.parentElement.querySelector('code').innerText;
        navigator.clipboard.writeText(code);
        this.innerHTML = 'Copied!';
        setTimeout(() => this.innerHTML = 'Copy', 2000);
    ">Copy</button>
    '''
    
    return f'''
    <div class="code-block">
        {copy_button}
        <pre><code class="{language}-code">{code}</code></pre>
    </div>
    '''

# Function to detect and format code in responses
def detect_and_format_code(text):
    # Check for Python code blocks with triple backticks
    code_blocks = re.findall(r'```(?:python)?(.*?)```', text, re.DOTALL)
    
    if code_blocks:
        for block in code_blocks:
            # Strip leading and trailing whitespace
            code = block.strip()
            formatted_code = format_code_block(code, "python")
            # Replace the code block with formatted HTML
            text = text.replace(f"```{block}```", formatted_code, 1)
            text = text.replace(f"```python{block}```", formatted_code, 1)
    
    # Check for inline code with single backticks
    inline_code = re.findall(r'`([^`]+)`', text)
    if inline_code:
        for code in inline_code:
            text = text.replace(f"`{code}`", f'<code style="background-color: #f1f1f1; padding: 2px 4px; border-radius: 4px;">{code}</code>', 1)
    
    return text

# Function to parse the LLM output with improved JSON handling
def parse_llm_response(response):
    """Parse the response from the LLM to extract action and action input with better JSON support."""
    try:
        # First try to parse as JSON directly
        if re.search(r'^\s*{.*}\s*$', response, re.DOTALL):
            try:
                parsed = json.loads(response)
                if isinstance(parsed, dict):
                    # Make sure keys are standardized
                    result = {}
                    for key in ["thought", "action", "action_input"]:
                        if key in parsed:
                            result[key] = parsed[key]
                        elif key.capitalize() in parsed:
                            result[key] = parsed[key.capitalize()]
                    
                    # Check for finish action
                    if result.get("action") == "FINISH" or result.get("action") == "Finish":
                        result["action"] = "FINISH"
                    
                    return result
            except json.JSONDecodeError:
                pass
        
        # Regular expression patterns with improved flexibility
        action_pattern = r"(?:Action|action):\s*(.*?)(?:\n|$)"
        action_input_pattern = r"(?:Action Input|action input|Action_Input|action_input):\s*(.*?)(?:\n|$)"
        thought_pattern = r"(?:Thought|thought):\s*(.*?)(?:\n|$)"
        finish_pattern = r"(FINISH|finish|Finish)"
        
        # Extract components
        action_match = re.search(action_pattern, response, re.DOTALL | re.IGNORECASE)
        action_input_match = re.search(action_input_pattern, response, re.DOTALL | re.IGNORECASE)
        thought_match = re.search(thought_pattern, response, re.DOTALL | re.IGNORECASE)
        finish_match = re.search(finish_pattern, response, re.IGNORECASE)
        
        action = action_match.group(1).strip() if action_match else None
        action_input = action_input_match.group(1).strip() if action_input_match else None
        thought = thought_match.group(1).strip() if thought_match else None
        
        # Check if finished
        if finish_match or (action and action.upper() == "FINISH"):
            return {"action": "FINISH", "action_input": thought or action_input or "Task completed."}
        
        # Ensure we have valid data
        if not action and "```" in response:
            # If response contains code but no action was detected, assume it's a Conversation action
            return {
                "thought": thought or "Processing code response",
                "action": "Conversation",
                "action_input": response
            }
        
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

FORMAT YOUR RESPONSE IN JSON:
{{
  "thought": "your reasoning about the current step",
  "action": "one of: Calculator, Conversation, FINISH",
  "action_input": "input for the action"
}}

If you can't format as JSON, use this alternative format:
Thought: [your reasoning about the current step]
Action: [one of: Calculator, Conversation, FINISH]
Action Input: [input for the action]

You are on step {step_count} of a max {st.session_state.max_steps} steps. Be efficient with your steps.
Always use the specified format to ensure I can parse your response.
When the task is complete, use "action": "FINISH" to end the process and provide a complete, comprehensive final answer.

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
            prompt += f"\nPlan: {', '.join(message['content'])}\n"
    
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
        return plan_steps or ["Analyze the query", "Provide a comprehensive response"]
    except Exception as e:
        return [f"Error generating plan: {str(e)}", "Proceeding with direct execution"]

# Display header
st.markdown('<h1>ReAct Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Solving tasks with reasoning and step-by-step execution</p>', unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    st.session_state.max_steps = st.slider("Max steps per query", 3, 15, 10)
    
    st.markdown("### Available Tools")
    st.markdown("- **Calculator**: Perform math calculations")
    st.markdown("- **Conversation**: Ask for clarification or follow-up")
    
    st.markdown("---")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.current_step = 0
        st.session_state.current_plan = []
        st.session_state.execution_started = False
        st.session_state.final_answers = []
        st.session_state.user_queries = []
        st.session_state.display_messages = []
        st.rerun()

# Create chat container
st.markdown('<div class="chat-container"><div class="messages-container">', unsafe_allow_html=True)

# Display messages in chat format
for msg in st.session_state.display_messages:
    role = msg["role"]
    content = msg["content"]
    
    if role == "user":
        st.markdown(f'<div class="message user"><div class="message-bubble">{content}</div></div>', unsafe_allow_html=True)
    elif role == "assistant":
        # Format the content with code highlighting if needed
        formatted_content = detect_and_format_code(content)
        st.markdown(f'<div class="message assistant"><div class="message-bubble">{formatted_content}</div></div>', unsafe_allow_html=True)
    elif role == "plan":
        # Create collapsible plan
        plan_steps = ""
        for step in content:
            plan_steps += f"<li>{step}</li>"
        
        st.markdown(f"""
        <div class="plan-container">
            <div class="plan-header">
                <span>Execution Plan</span>
                <span class="expand-icon">+</span>
            </div>
            <div class="plan-content">
                <ol class="plan-steps">
                    {plan_steps}
                </ol>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif role == "tool":
        st.markdown(f'<div class="tool-output">{content}</div>', unsafe_allow_html=True)

# Show thinking animation if processing
if st.session_state.is_processing:
    st.markdown('<div class="thinking">Thinking</div>', unsafe_allow_html=True)

# Close messages container
st.markdown('</div>', unsafe_allow_html=True)

# User input
user_query = st.text_input("", placeholder="What can I help you with today?", key="user_input")

# Add a "Send" button
send_button = st.button("Send")

# Process user query
if user_query and send_button:
    # Add user message to display messages
    st.session_state.display_messages.append({"role": "user", "content": user_query})
    st.session_state.user_queries.append(user_query)
    
    # Add to internal message history
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Reset execution state for new query
    st.session_state.current_step = 0
    st.session_state.execution_started = False
    st.session_state.current_plan = []
    st.session_state.is_processing = True
    
    # Generate plan (but don't display immediately)
    plan_steps = generate_plan(user_query)
    st.session_state.current_plan = plan_steps
    
    # Add plan to internal message history (not display messages)
    st.session_state.messages.append({"role": "plan", "content": plan_steps})
    
    # Set execution flag
    st.session_state.execution_started = True
    
    # Clear input
    st.session_state.user_input = ""
    
    # Rerun to update UI
    st.rerun()

# Execute plan if needed (but don't show intermediate steps)
if st.session_state.execution_started and st.session_state.current_step < st.session_state.max_steps:
    st.session_state.is_processing = True
    
    # Generate prompt and get LLM response
    prompt = generate_prompt(
        user_query=st.session_state.user_queries[-1],
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
            # Add error message to display messages
            error_msg = f"I encountered an error while processing your request. Please try again or rephrase your question."
            st.session_state.display_messages.append({"role": "assistant", "content": error_msg})
            st.session_state.execution_started = False
            st.session_state.is_processing = False
        else:
            # Process the action
            action = parsed_response.get("action")
            action_input = parsed_response.get("action_input")
            thought = parsed_response.get("thought", "")
            
            # Store thought in internal messages but don't display
            if thought:
                st.session_state.messages.append({"role": "assistant", "content": f"Thought: {thought}"})
            
            # Handle different actions
            if action == "Calculator":
                # Execute calculator
                result = calculator_tool(action_input)
                
                # Add to internal history (not display)
                st.session_state.messages.append({"role": "tool", "tool": "Calculator", "content": result})
            
            elif action == "Conversation" and not action == "FINISH":
                # Only store intermediate conversations in internal history
                st.session_state.messages.append({"role": "assistant", "content": action_input})
            
            elif action == "FINISH":
                # Format the final answer
                formatted_content = action_input
                
                # Add to display messages (this is what the user will see)
                st.session_state.display_messages.append({"role": "assistant", "content": formatted_content})
                
                # Add to internal history
                st.session_state.messages.append({"role": "assistant", "content": formatted_content})
                
                # Add plan to display messages (as collapsible)
                st.session_state.display_messages.append({"role": "plan", "content": st.session_state.current_plan})
                
                # End execution
                st.session_state.execution_started = False
                st.session_state.is_processing = False
            
            # Increment step counter
            st.session_state.current_step += 1
            
            # Check if max steps reached
            if st.session_state.current_step >= st.session_state.max_steps:
                # If max steps reached without finishing, show a message and end
                st.session_state.display_messages.append({
                    "role": "assistant", 
                    "content": "I've analyzed your request but couldn't complete it within the step limit. Here's what I've found so far..."
                })
                st.session_state.execution_started = False
                st.session_state.is_processing = False
            
            # Rerun if still executing
            if st.session_state.execution_started:
                time.sleep(0.1)  # Small delay
                st.rerun()
            else:
                # When execution is finished, rerun one last time to update UI
                st.rerun()
    
    except Exception as e:
        # Handle any errors
        st.session_state.display_messages.append({
            "role": "assistant", 
            "content": f"I encountered an error while processing your request. Please try again or rephrase your question."
        })
        st.session_state.execution_started = False
        st.session_state.is_processing = False
        st.rerun()

# Close chat container
st.markdown('</div>', unsafe_allow_html=True)
