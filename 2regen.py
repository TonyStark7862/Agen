import streamlit as st
import json
import re
import time
import base64
from abc_response import abc_response  # Import your LLM function

# Set page configuration
st.set_page_config(
    page_title="ReAct Agent",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS for professional UI
st.markdown("""
<style>
/* Global styles */
.main {
    background-color: #f9f9f9;
    padding: 20px;
}

/* Header styles */
h1 {
    color: #1e3a8a;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-weight: 600;
}

/* Message container styles */
.chat-container {
    max-width: 800px;
    margin: 0 auto;
}

.chat-message {
    padding: 1.2rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    display: flex;
    flex-direction: column;
    max-width: 80%;
    border-left: 4px solid transparent;
}

.chat-message.user {
    background-color: #f0f2f6;
    border-left-color: #1e3a8a;
    margin-left: auto;
    border-bottom-right-radius: 0;
    text-align: right;
}

.chat-message.assistant {
    background-color: #eef4ff;
    border-left-color: #3b82f6;
    margin-right: auto;
    border-bottom-left-radius: 0;
    text-align: left;
}

.chat-message.tool {
    background-color: #ecfdf5;
    border-left-color: #059669;
    margin-right: auto;
    border-bottom-left-radius: 0;
}

.chat-message.plan {
    background-color: #fef3c7;
    border-left-color: #d97706;
    margin-right: auto;
    width: 100%;
    max-width: 100%;
}

.message-header {
    width: 100%;
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #4b5563;
}

.message-content {
    width: 100%;
}

/* Plan styles */
.plan-container {
    background-color: #fffbeb;
    border: 1px solid #fbbf24;
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 1rem;
}

.plan-header {
    font-weight: 600;
    color: #92400e;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
}

.plan-steps {
    margin-left: 1.5rem;
}

/* Thought container styles */
.thought-container {
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    overflow: hidden;
}

.thought-header {
    padding: 0.75rem 1rem;
    background-color: #f3f4f6;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.thought-content {
    padding: 1rem;
    border-top: 1px solid #e5e7eb;
    background-color: #ffffff;
}

/* Step counter styles */
.step-counter {
    background-color: #3b82f6;
    color: white;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-right: 8px;
    font-size: 14px;
    flex-shrink: 0;
}

/* Code block styles */
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

.code-header {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 1rem;
    background-color: #252526;
    border-top-left-radius: 0.5rem;
    border-top-right-radius: 0.5rem;
    color: #ffffff;
    font-size: 0.875rem;
}

.copy-button {
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.25rem;
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    cursor: pointer;
    position: absolute;
    right: 0.5rem;
    top: 0.5rem;
}

.copy-button:hover {
    background-color: #2563eb;
}

/* Thinking animation */
.thinking {
    color: #6b7280;
    font-style: italic;
    display: flex;
    align-items: center;
}

.thinking::after {
    content: '';
    width: 16px;
    height: 16px;
    margin-left: 8px;
    border: 2px solid #d1d5db;
    border-radius: 50%;
    border-top-color: #3b82f6;
    animation: spinner 1s linear infinite;
}

@keyframes spinner {
    to {transform: rotate(360deg);}
}

/* Buttons and inputs */
.stButton button {
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.25rem;
    font-weight: 500;
}

.stButton button:hover {
    background-color: #2563eb;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {
    visibility: hidden;
}

/* Enhance readability of markdown */
.markdown-text-container {
    line-height: 1.6;
}

/* Scrollable response content for long outputs */
.scrollable-content {
    max-height: 300px;
    overflow-y: auto;
    padding-right: 10px;
    border: 1px solid #e5e7eb;
    border-radius: 0.25rem;
}

/* Syntax highlighting for code blocks */
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
</style>
""", unsafe_allow_html=True)

# Function to create collapsible sections
def create_collapsible(header, content, is_open=False, key=None):
    # Generate a unique key if none provided
    if key is None:
        key = base64.b64encode(f"{header}{time.time()}".encode()).decode()
    
    # Create the collapsible UI
    is_expanded = st.checkbox(header, value=is_open, key=f"expand_{key}")
    
    if is_expanded:
        st.markdown(f'<div class="thought-content">{content}</div>', unsafe_allow_html=True)
    
    return is_expanded

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
if "thoughts" not in st.session_state:
    st.session_state.thoughts = []
if "answers" not in st.session_state:
    st.session_state.answers = []

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
        return f"Calculator result: {result}"
    except Exception as e:
        return f"Calculator error: {str(e)}"

# Display header
st.markdown('<h1 style="text-align: center;">ReAct Agent</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #6b7280;">Solving tasks with reasoning and step-by-step execution</p>', unsafe_allow_html=True)

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
        st.session_state.thoughts = []
        st.session_state.answers = []
        st.rerun()

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
        if re.search(r'^\s*{.*}\s*
        
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
When the task is complete, use "action": "FINISH" to end the process.

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

# Function to display chat messages with improved formatting
def display_message(role, content, tool=None, step=None, is_thought=False):
    # Determine message class
    message_class = "thought-container" if is_thought else f"chat-message {role}"
    
    # Format code in content if present
    formatted_content = detect_and_format_code(content)
    
    # Determine header text
    if is_thought:
        header = f"Reasoning (Step {step})" if step else "Reasoning"
        
        # Create collapsible thought
        with st.container():
            st.markdown(f"""
            <div class="thought-container">
                <div class="thought-header" id="thought-header-{step}">
                    {header}
                    <span class="expand-icon">+</span>
                </div>
                <div class="thought-content" style="display: none;">
                    {formatted_content}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add JavaScript to toggle visibility
            st.markdown(f"""
            <script>
                const header = document.getElementById('thought-header-{step}');
                if (header) {{
                    header.addEventListener('click', function() {{
                        const content = this.nextElementSibling;
                        if (content.style.display === 'none') {{
                            content.style.display = 'block';
                            this.querySelector('.expand-icon').textContent = '-';
                        }} else {{
                            content.style.display = 'none';
                            this.querySelector('.expand-icon').textContent = '+';
                        }}
                    }});
                }}
            </script>
            """, unsafe_allow_html=True)
    else:
        # For regular messages
        with st.container():
            # Only show step for Final Answer or when explicitly requested
            header_text = ""
            if role == "tool":
                header_text = f"Tool ({tool})"
            elif step is not None and ("Final Answer" in content or "Step" in content):
                header_text = f"Step {step}"
            elif role == "user":
                header_text = ""  # No header for user messages
            else:
                header_text = ""  # No header for assistant normal messages
            
            header_html = f'<div class="message-header">{header_text}</div>' if header_text else ""
            
            st.markdown(f"""
            <div class="chat-message {role}">
                {header_html}
                <div class="message-content">
                    {formatted_content}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Function to display the plan
def display_plan(plan_steps):
    steps_html = ""
    for i, step in enumerate(plan_steps):
        steps_html += f"<li>{step}</li>"
    
    st.markdown(f"""
    <div class="plan-container">
        <div class="plan-header">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            Execution Plan
        </div>
        <ol class="plan-steps">
            {steps_html}
        </ol>
    </div>
    """, unsafe_allow_html=True)

# Display thoughts in a collapsible section
def display_thoughts():
    if st.session_state.thoughts:
        with st.expander("View Reasoning Process", expanded=False):
            for i, thought in enumerate(st.session_state.thoughts):
                st.markdown(f"**Step {i+1}**: {thought}")

# Display all answers as a continuous response
def display_answers():
    if st.session_state.answers:
        for answer in st.session_state.answers:
            st.markdown(detect_and_format_code(answer), unsafe_allow_html=True)

# Display chat history
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Collect and organize message data
user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
plans = [msg for msg in st.session_state.messages if msg["role"] == "plan"]
thoughts = []
answers = []
step_counter = 0

# First pass - collect thoughts and show user messages
for message in st.session_state.messages:
    if message["role"] == "user":
        display_message("user", message["content"])
    elif message["role"] == "plan":
        display_plan(message["content"])
    elif message["role"] == "assistant" and "Thought" in message["content"]:
        # Collect thoughts for collapsible section
        thought_content = message["content"].replace("Thought: ", "")
        thoughts.append(thought_content)
        step_counter += 1
        display_message("assistant", thought_content, is_thought=True, step=step_counter)
    elif message["role"] == "tool":
        # Don't display tools here, they'll be shown after thoughts
        pass
    elif message["role"] == "assistant":
        # Don't display assistant messages here, they'll be shown after thoughts
        answers.append(message["content"])

# Second pass - display tool outputs and assistant answers with step numbers
current_step = 0
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "tool":
        current_step += 1
        display_message("tool", message["content"], tool=message["tool"], step=current_step)
    elif message["role"] == "assistant" and "Thought" not in message["content"] and "Final Answer" not in message["content"]:
        current_step += 1
        display_message("assistant", message["content"], step=current_step)
    elif message["role"] == "assistant" and "Final Answer" in message["content"]:
        current_step += 1
        display_message("assistant", message["content"], step=current_step)

st.markdown('</div>', unsafe_allow_html=True)

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
    st.session_state.thoughts = []
    st.session_state.answers = []
    
    # Show thinking indicator
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown('<div class="thinking">Generating plan...</div>', unsafe_allow_html=True)
    
    # Generate plan
    plan_steps = generate_plan(user_query)
    st.session_state.current_plan = plan_steps
    
    # Add plan to chat history
    st.session_state.messages.append({"role": "plan", "content": plan_steps})
    
    # Display plan
    thinking_placeholder.empty()
    display_plan(plan_steps)
    
    # Set execution flag
    st.session_state.execution_started = True
    st.experimental_rerun()

# Execute plan if needed
if st.session_state.execution_started and st.session_state.current_step < st.session_state.max_steps:
    # Show thinking indicator for execution
    execution_placeholder = st.empty()
    execution_placeholder.markdown(f'<div class="thinking">Executing step {st.session_state.current_step + 1}...</div>', unsafe_allow_html=True)
    
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
                # Save thought to session state
                st.session_state.thoughts.append(thought)
                
                # Add to message history
                thought_message = f"Thought: {thought}"
                st.session_state.messages.append({"role": "assistant", "content": thought_message})
                
                # Display as collapsible
                display_message("assistant", thought, is_thought=True, step=st.session_state.current_step + 1)
            
            # Handle different actions
            if action == "Calculator":
                # Execute calculator
                result = calculator_tool(action_input)
                
                # Display in UI
                display_message("assistant", f"Using calculator to compute: {action_input}", step=st.session_state.current_step + 1)
                display_message("tool", result, tool="Calculator")
                
                # Add to history
                st.session_state.messages.append({"role": "tool", "tool": "Calculator", "content": result})
            
            elif action == "Conversation":
                # Format the response content
                formatted_content = detect_and_format_code(action_input)
                
                # Save to answers
                st.session_state.answers.append(formatted_content)
                
                # Display conversation response
                display_message("assistant", action_input, step=st.session_state.current_step + 1)
                
                # Add to history
                st.session_state.messages.append({"role": "assistant", "content": action_input})
            
            elif action == "FINISH":
                # Format the final answer
                formatted_content = detect_and_format_code(action_input)
                
                # Save to answers
                st.session_state.answers.append(formatted_content)
                
                # Display final response
                display_message("assistant", f"Final Answer: {action_input}", step=st.session_state.current_step + 1)
                
                # Add to history
                st.session_state.messages.append({"role": "assistant", "content": f"Final Answer: {action_input}"})
                
                # End execution
                st.session_state.execution_started = False
            
            # Increment step counter
            st.session_state.current_step += 1
            
            # Check if max steps reached
            if st.session_state.current_step >= st.session_state.max_steps:
                display_message("assistant", "Maximum number of steps reached. Stopping execution.", step=st.session_state.current_step)
                st.session_state.messages.append({"role": "assistant", "content": "Maximum number of steps reached."})
                st.session_state.execution_started = False
            
            # Clear thinking indicator
            execution_placeholder.empty()
            
            # Rerun if still executing
            if st.session_state.execution_started:
                time.sleep(0.5)  # Small delay for better UX
                st.experimental_rerun()
    
    except Exception as e:
        st.error(f"Error during execution: {str(e)}")
        st.session_state.execution_started = False
        execution_placeholder.empty()
, response, re.DOTALL):
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
                    
                    # Handle Python code in action_input
                    if "action_input" in result and "```python" in result["action_input"]:
                        # Extract and format Python code
                        code_blocks = re.findall(r'```(?:python)?(.*?)```', result["action_input"], re.DOTALL)
                        if code_blocks:
                            result["action_input"] = result["action_input"]  # Keep as is, will be formatted later
                    
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
When the task is complete, use "action": "FINISH" to end the process.

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

# Function to display chat messages with improved formatting
def display_message(role, content, tool=None, step=None, is_thought=False):
    # Determine message class
    message_class = "thought-container" if is_thought else f"chat-message {role}"
    
    # Format code in content if present
    formatted_content = detect_and_format_code(content)
    
    # Determine header text
    if is_thought:
        header = f"Reasoning (Step {step})" if step else "Reasoning"
        
        # Create collapsible thought
        with st.container():
            st.markdown(f"""
            <div class="thought-container">
                <div class="thought-header" id="thought-header-{step}">
                    {header}
                    <span class="expand-icon">+</span>
                </div>
                <div class="thought-content" style="display: none;">
                    {formatted_content}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add JavaScript to toggle visibility
            st.markdown(f"""
            <script>
                const header = document.getElementById('thought-header-{step}');
                if (header) {{
                    header.addEventListener('click', function() {{
                        const content = this.nextElementSibling;
                        if (content.style.display === 'none') {{
                            content.style.display = 'block';
                            this.querySelector('.expand-icon').textContent = '-';
                        }} else {{
                            content.style.display = 'none';
                            this.querySelector('.expand-icon').textContent = '+';
                        }}
                    }});
                }}
            </script>
            """, unsafe_allow_html=True)
    else:
        # For regular messages
        with st.container():
            # Only show step for Final Answer or when explicitly requested
            header_text = ""
            if role == "tool":
                header_text = f"Tool ({tool})"
            elif step is not None and ("Final Answer" in content or "Step" in content):
                header_text = f"Step {step}"
            elif role == "user":
                header_text = ""  # No header for user messages
            else:
                header_text = ""  # No header for assistant normal messages
            
            header_html = f'<div class="message-header">{header_text}</div>' if header_text else ""
            
            st.markdown(f"""
            <div class="chat-message {role}">
                {header_html}
                <div class="message-content">
                    {formatted_content}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Function to display the plan
def display_plan(plan_steps):
    steps_html = ""
    for i, step in enumerate(plan_steps):
        steps_html += f"<li>{step}</li>"
    
    st.markdown(f"""
    <div class="plan-container">
        <div class="plan-header">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            Execution Plan
        </div>
        <ol class="plan-steps">
            {steps_html}
        </ol>
    </div>
    """, unsafe_allow_html=True)

# Display thoughts in a collapsible section
def display_thoughts():
    if st.session_state.thoughts:
        with st.expander("View Reasoning Process", expanded=False):
            for i, thought in enumerate(st.session_state.thoughts):
                st.markdown(f"**Step {i+1}**: {thought}")

# Display all answers as a continuous response
def display_answers():
    if st.session_state.answers:
        for answer in st.session_state.answers:
            st.markdown(detect_and_format_code(answer), unsafe_allow_html=True)

# Display chat history
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Collect and organize message data
user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
plans = [msg for msg in st.session_state.messages if msg["role"] == "plan"]
thoughts = []
answers = []
step_counter = 0

# First pass - collect thoughts and show user messages
for message in st.session_state.messages:
    if message["role"] == "user":
        display_message("user", message["content"])
    elif message["role"] == "plan":
        display_plan(message["content"])
    elif message["role"] == "assistant" and "Thought" in message["content"]:
        # Collect thoughts for collapsible section
        thought_content = message["content"].replace("Thought: ", "")
        thoughts.append(thought_content)
        step_counter += 1
        display_message("assistant", thought_content, is_thought=True, step=step_counter)
    elif message["role"] == "tool":
        # Don't display tools here, they'll be shown after thoughts
        pass
    elif message["role"] == "assistant":
        # Don't display assistant messages here, they'll be shown after thoughts
        answers.append(message["content"])

# Second pass - display tool outputs and assistant answers with step numbers
current_step = 0
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "tool":
        current_step += 1
        display_message("tool", message["content"], tool=message["tool"], step=current_step)
    elif message["role"] == "assistant" and "Thought" not in message["content"] and "Final Answer" not in message["content"]:
        current_step += 1
        display_message("assistant", message["content"], step=current_step)
    elif message["role"] == "assistant" and "Final Answer" in message["content"]:
        current_step += 1
        display_message("assistant", message["content"], step=current_step)

st.markdown('</div>', unsafe_allow_html=True)

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
    st.session_state.thoughts = []
    st.session_state.answers = []
    
    # Show thinking indicator
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown('<div class="thinking">Generating plan...</div>', unsafe_allow_html=True)
    
    # Generate plan
    plan_steps = generate_plan(user_query)
    st.session_state.current_plan = plan_steps
    
    # Add plan to chat history
    st.session_state.messages.append({"role": "plan", "content": plan_steps})
    
    # Display plan
    thinking_placeholder.empty()
    display_plan(plan_steps)
    
    # Set execution flag
    st.session_state.execution_started = True
    st.experimental_rerun()

# Execute plan if needed
if st.session_state.execution_started and st.session_state.current_step < st.session_state.max_steps:
    # Show thinking indicator for execution
    execution_placeholder = st.empty()
    execution_placeholder.markdown(f'<div class="thinking">Executing step {st.session_state.current_step + 1}...</div>', unsafe_allow_html=True)
    
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
                # Save thought to session state
                st.session_state.thoughts.append(thought)
                
                # Add to message history
                thought_message = f"Thought: {thought}"
                st.session_state.messages.append({"role": "assistant", "content": thought_message})
                
                # Display as collapsible
                display_message("assistant", thought, is_thought=True, step=st.session_state.current_step + 1)
            
            # Handle different actions
            if action == "Calculator":
                # Execute calculator
                result = calculator_tool(action_input)
                
                # Display in UI
                display_message("assistant", f"Using calculator to compute: {action_input}", step=st.session_state.current_step + 1)
                display_message("tool", result, tool="Calculator")
                
                # Add to history
                st.session_state.messages.append({"role": "tool", "tool": "Calculator", "content": result})
            
            elif action == "Conversation":
                # Format the response content
                formatted_content = detect_and_format_code(action_input)
                
                # Save to answers
                st.session_state.answers.append(formatted_content)
                
                # Display conversation response
                display_message("assistant", action_input, step=st.session_state.current_step + 1)
                
                # Add to history
                st.session_state.messages.append({"role": "assistant", "content": action_input})
            
            elif action == "FINISH":
                # Format the final answer
                formatted_content = detect_and_format_code(action_input)
                
                # Save to answers
                st.session_state.answers.append(formatted_content)
                
                # Display final response
                display_message("assistant", f"Final Answer: {action_input}", step=st.session_state.current_step + 1)
                
                # Add to history
                st.session_state.messages.append({"role": "assistant", "content": f"Final Answer: {action_input}"})
                
                # End execution
                st.session_state.execution_started = False
            
            # Increment step counter
            st.session_state.current_step += 1
            
            # Check if max steps reached
            if st.session_state.current_step >= st.session_state.max_steps:
                display_message("assistant", "Maximum number of steps reached. Stopping execution.", step=st.session_state.current_step)
                st.session_state.messages.append({"role": "assistant", "content": "Maximum number of steps reached."})
                st.session_state.execution_started = False
            
            # Clear thinking indicator
            execution_placeholder.empty()
            
            # Rerun if still executing
            if st.session_state.execution_started:
                time.sleep(0.5)  # Small delay for better UX
                st.experimental_rerun()
    
    except Exception as e:
        st.error(f"Error during execution: {str(e)}")
        st.session_state.execution_started = False
        execution_placeholder.empty()
