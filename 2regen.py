import streamlit as st
import json
import re
import base64
from datetime import datetime
import uuid
import os

# --------------------
# ---- CONFIG ----
# --------------------
st.set_page_config(
    page_title="React Agent", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------
# ---- HELPER FUNCTIONS ----
# --------------------
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --------------------
# ---- STYLES ----
# --------------------
st.markdown("""
    <style>
        /* Global Styles */
        body {
            font-family: 'Inter', sans-serif;
            background-color: #F9F9F9;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Chat container */
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 16px;
            padding-bottom: 80px;
            min-height: calc(100vh - 200px);
        }
        
        /* Message bubbles */
        .msg {
            padding: 14px 18px;
            border-radius: 18px;
            max-width: 80%;
            line-height: 1.5;
            white-space: pre-wrap;
            overflow-wrap: break-word;
        }
        
        .user-msg-container {
            display: flex;
            justify-content: flex-end;
            margin: 8px 0;
        }
        
        .user-msg {
            background: #ffffff;
            border: 1px solid #E53935;
            border-radius: 18px 18px 0 18px;
            color: #333333;
            align-self: flex-end;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        
        .agent-msg-container {
            display: flex;
            justify-content: flex-start;
            margin: 8px 0;
        }
        
        .agent-msg {
            background: #FFEBEE;
            border: 1px solid #FFCDD2;
            border-radius: 18px 18px 18px 0;
            color: #333333;
            align-self: flex-start;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        
        /* Thought process */
        .thought-container {
            background: #FFFFFF;
            border: 1px solid #EEEEEE;
            border-radius: 8px;
            margin: 10px 0;
            overflow: hidden;
        }
        
        .thought-header {
            background: #FFEBEE;
            padding: 10px 15px;
            font-weight: 600;
            color: #E53935;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }
        
        .thought-body {
            padding: 0 15px;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }
        
        .thought-body.expanded {
            max-height: 1000px;
            padding: 15px;
        }
        
        .thought {
            background: #F9F9F9;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 3px solid #FFCDD2;
        }
        
        .action {
            background: #F9F9F9;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 3px solid #E53935;
        }
        
        .observation {
            background: #F9F9F9;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 3px solid #C62828;
        }
        
        /* Input area */
        .input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            padding: 15px 20px;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
            z-index: 1000;
            display: flex;
            justify-content: center;
        }
        
        .input-box {
            display: flex;
            width: 90%;
            max-width: 1200px;
            background: white;
            border: 1px solid #E0E0E0;
            border-radius: 24px;
            padding: 6px;
        }
        
        .input-field {
            flex-grow: 1;
            border: none;
            padding: 10px 15px;
            outline: none;
            font-size: 16px;
            background: transparent;
        }
        
        .upload-btn {
            background: #F5F5F5;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            margin-right: 5px;
        }
        
        .upload-btn:hover {
            background: #EEEEEE;
        }
        
        .send-btn {
            background: #E53935;
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
        
        .send-btn:disabled {
            background: #FFCDD2;
            cursor: not-allowed;
        }
        
        /* Status bar */
        .status-bar {
            position: sticky;
            top: 0;
            background: white;
            padding: 10px 15px;
            border-bottom: 1px solid #EEEEEE;
            z-index: 100;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 14px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4CAF50;
        }
        
        .status-steps {
            background: #F5F5F5;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            color: #757575;
        }
        
        /* Typing indicator */
        .typing-indicator {
            display: flex;
            align-items: center;
            padding: 14px 18px;
            background: #FFEBEE;
            border: 1px solid #FFCDD2;
            border-radius: 18px 18px 18px 0;
            align-self: flex-start;
            max-width: 100px;
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #E53935;
            margin: 0 2px;
            animation: typing-animation 1.2s infinite;
            opacity: 0.6;
        }
        
        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes typing-animation {
            0% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0); }
        }
        
        /* File upload preview */
        .file-preview {
            background: #F9F9F9;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .file-icon {
            background: #E53935;
            color: white;
            border-radius: 8px;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        
        .file-info {
            flex-grow: 1;
        }
        
        .file-name {
            font-weight: 600;
            margin-bottom: 2px;
        }
        
        .file-size {
            font-size: 12px;
            color: #757575;
        }
        
        /* Tool cards */
        .tools-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .tool-card {
            background: white;
            border: 1px solid #EEEEEE;
            border-radius: 8px;
            padding: 15px;
            transition: all 0.2s ease;
        }
        
        .tool-card:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            border-color: #FFCDD2;
        }
        
        .tool-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }
        
        .tool-icon {
            background: #FFEBEE;
            color: #E53935;
            border-radius: 8px;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .tool-title {
            font-weight: 600;
            color: #333333;
        }
        
        .tool-description {
            font-size: 14px;
            color: #757575;
            margin-bottom: 10px;
        }
        
        /* Settings */
        .settings-section {
            background: white;
            border: 1px solid #EEEEEE;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .settings-header {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333333;
        }
        
        /* Icons */
        .icon-plus {
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .icon-plus:before,
        .icon-plus:after {
            content: "";
            position: absolute;
            background: #757575;
        }
        
        .icon-plus:before {
            width: 12px;
            height: 2px;
        }
        
        .icon-plus:after {
            width: 2px;
            height: 12px;
        }
        
        .icon-send {
            width: 16px;
            height: 16px;
            border: solid 2px white;
            border-radius: 50%;
            position: relative;
        }
        
        .icon-send:after {
            content: "";
            position: absolute;
            top: 3px;
            left: 10px;
            width: 8px;
            height: 8px;
            border-top: 2px solid white;
            border-right: 2px solid white;
            transform: rotate(45deg);
        }
    </style>
    
    <style>
        /* Custom file input */
        .custom-file-upload {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# --------------------
# ---- ICONS ----
# --------------------
plus_icon = """
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#757575" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="12" y1="5" x2="12" y2="19"></line>
    <line x1="5" y1="12" x2="19" y2="12"></line>
</svg>
"""

send_icon = """
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="22" y1="2" x2="11" y2="13"></line>
    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
</svg>
"""

file_icon = """
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#757575" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
    <polyline points="13 2 13 9 20 9"></polyline>
</svg>
"""

chevron_down = """
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#E53935" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="6 9 12 15 18 9"></polyline>
</svg>
"""

# --------------------
# ---- SESSION STATE ----
# --------------------
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

if "history" not in st.session_state:
    st.session_state.history = []

if "agent_steps" not in st.session_state:
    st.session_state.agent_steps = []

if "step_count" not in st.session_state:
    st.session_state.step_count = 0

if "max_steps" not in st.session_state:
    st.session_state.max_steps = 10

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "typing" not in st.session_state:
    st.session_state.typing = False

if "expanded_thoughts" not in st.session_state:
    st.session_state.expanded_thoughts = set()

if "show_thoughts" not in st.session_state:
    st.session_state.show_thoughts = True

# --------------------
# ---- BUILT-IN TOOLS ----
# --------------------
def calculator_tool(prompt):
    try:
        # Clean the input to only allow safe math expressions
        expr = re.findall(r"[-+*/().0-9 ]+", prompt)
        expr = "".join(expr)
        result = eval(expr, {"__builtins__": None})
        return f"The result of {expr} is {result}"
    except Exception as e:
        return f"Invalid calculation. Error: {str(e)}"

def python_executor(code):
    try:
        # Prepare a safe execution environment
        exec_globals = {}
        
        # Execute the code and capture outputs
        exec(code, exec_globals)
        
        # Check if 'result' is set in the global namespace
        if "result" in exec_globals:
            return f"Code executed successfully. Result: {exec_globals['result']}"
        else:
            return "Code executed successfully but no 'result' variable was found."
    except Exception as e:
        return f"Error executing Python code: {str(e)}"

def file_preview_tool(file_name=None):
    if not st.session_state.uploaded_files:
        return "No files have been uploaded."
    
    # If filename is specified, find that file
    if file_name:
        for file in st.session_state.uploaded_files:
            if file.name.lower() == file_name.lower():
                return _process_file_preview(file)
        return f"File '{file_name}' not found. Available files: {', '.join([f.name for f in st.session_state.uploaded_files])}"
    
    # Otherwise, preview the most recently uploaded file
    return _process_file_preview(st.session_state.uploaded_files[-1])

def _process_file_preview(file):
    try:
        # Get file extension
        file_ext = os.path.splitext(file.name)[1].lower()
        
        # Handle different file types
        if file_ext in ['.csv', '.txt']:
            # Read as text
            content = file.getvalue().decode("utf-8").splitlines()
            preview = "\n".join(content[:10])  # First 10 lines
            return f"File: {file.name}\nSize: {len(file.getvalue())} bytes\nPreview:\n{preview}\n...(truncated)"
        
        elif file_ext in ['.json']:
            # Read as JSON
            content = json.loads(file.getvalue().decode("utf-8"))
            preview = json.dumps(content, indent=2)[:500]  # First 500 chars
            return f"File: {file.name}\nSize: {len(file.getvalue())} bytes\nPreview:\n{preview}\n...(truncated)"
        
        else:
            # Generic binary file
            return f"File: {file.name}\nSize: {len(file.getvalue())} bytes\nType: Binary file"
    except Exception as e:
        return f"Error previewing file: {str(e)}"

def conversation_tool(prompt):
    return prompt

def list_files_tool():
    if not st.session_state.uploaded_files:
        return "No files have been uploaded."
    
    file_list = []
    for idx, file in enumerate(st.session_state.uploaded_files):
        file_list.append(f"{idx+1}. {file.name} ({len(file.getvalue())} bytes)")
    
    return "Uploaded files:\n" + "\n".join(file_list)

# Tool registry
BUILT_IN_TOOLS = {
    "calculator": {
        "name": "calculator",
        "description": "Evaluate mathematical expressions",
        "function": calculator_tool
    },
    "conversation": {
        "name": "conversation",
        "description": "General conversation, follow-ups, asking clarifying questions",
        "function": conversation_tool
    },
    "python_executor": {
        "name": "python_executor",
        "description": "Execute Python code to solve problems",
        "function": python_executor
    },
    "file_preview": {
        "name": "file_preview",
        "description": "Preview contents of uploaded files",
        "function": file_preview_tool
    },
    "list_files": {
        "name": "list_files",
        "description": "List all uploaded files",
        "function": list_files_tool
    }
}

# --------------------
# ---- SAFE JSON PARSER ----
# --------------------
def safe_json_extract(text):
    """
    Robustly extract JSON from text that may include explanations or code blocks.
    """
    try:
        # First try direct JSON parsing
        text = text.strip()
        return json.loads(text)
    except:
        try:
            # Try to extract JSON from code blocks
            if "```json" in text.lower() or "```" in text:
                # Extract content from code block
                pattern = r"```(?:json)?\s*([\s\S]*?)```"
                match = re.search(pattern, text, re.MULTILINE)
                if match:
                    return json.loads(match.group(1).strip())
            
            # Try to extract JSON objects with regex
            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                return json.loads(match.group(0))
            
            return {"action": "conversation", "action_input": "I couldn't understand the last message properly. Could you please clarify?"}
        except Exception as e:
            # Fallback for when JSON extraction fails
            return {"action": "conversation", "action_input": f"I encountered an error processing your request. Could you please rephrase?"}

# --------------------
# ---- AGENT STEP ----
# --------------------
def agent_step(user_input, prev_observation=None):
    """
    Single step of the ReAct agent loop.
    """
    # Increment step counter
    st.session_state.step_count += 1
    
    # Check for file references in the user input
    file_context = ""
    if st.session_state.uploaded_files and any(file.name.lower() in user_input.lower() for file in st.session_state.uploaded_files):
        # User mentioned a file by name - add context
        file_context = "\nFile context: " + list_files_tool()
    
    # Build tool descriptions
    tool_descriptions = []
    for tool_id, tool in BUILT_IN_TOOLS.items():
        tool_descriptions.append(f"- {tool['name']}: {tool['description']}")
    
    tool_descriptions_text = "\n".join(tool_descriptions)
    
    # Build the prompt
    agent_prompt = f"""[System]
You are a ReAct Agent that follows the Thought-Action-Observation pattern to answer user queries.
Your goal is to answer the user's question using minimal steps and minimal tools.

[Current Step]: {st.session_state.step_count}
[Step Limit]: {st.session_state.max_steps} (you should try to complete the task in fewer steps when possible)
[Previous Observation]: {prev_observation or "None"}

[Available Tools]:
{tool_descriptions_text}
{file_context}

Always respond using ONLY the following JSON format (no other text before or after):
{{
  "thought": "your detailed reasoning about what to do next",
  "action": "tool_name",
  "action_input": "input for the selected tool"
}}

You can also finish the conversation with:
{{
  "action": "finish",
  "thought": "why you are finishing"
}}

[User]: {user_input}
"""

    # Set typing indicator
    st.session_state.typing = True
    st.experimental_rerun()  # Show typing indicator
    
    # Call the LLM
    response = abc_response(agent_prompt)
    
    # Parse the response
    parsed = safe_json_extract(response)
    
    # Check if we need to finish
    if parsed.get("action") == "finish" or st.session_state.step_count >= st.session_state.max_steps:
        st.session_state.step_count = 0
        
        # Create final thought record
        thought = parsed.get("thought", "Task completed.")
        return {
            "thought": thought,
            "action": "finish", 
            "observation": "I've completed the task."
        }
    
    # Execute the tool
    tool_name = parsed.get("action", "conversation")
    action_input = parsed.get("action_input", "")
    
    if tool_name in BUILT_IN_TOOLS:
        observation = BUILT_IN_TOOLS[tool_name]["function"](action_input)
    else:
        # Fallback to conversation if tool not found
        observation = f"Tool '{tool_name}' not found. Available tools: {', '.join(BUILT_IN_TOOLS.keys())}"
        tool_name = "conversation"
    
    # Return step results
    return {
        "thought": parsed.get("thought", ""),
        "action": tool_name,
        "action_input": action_input,
        "observation": observation
    }

# --------------------
# ---- LLM INTEGRATION ----
# --------------------
def abc_response(prompt):
    """
    Placeholder for the LLM integration.
    In a real implementation, this would call an LLM API.
    """
    # Simulate response - in a real implementation, this would be replaced with your LLM API call
    return """
{
  "thought": "I should greet the user and ask how I can help them today.",
  "action": "conversation",
  "action_input": "Hello! I'm your ReAct Agent. How can I assist you today?"
}
"""

# --------------------
# ---- AGENT LOOP ----
# --------------------
def run_agent_loop(user_input):
    """
    Run the full agent loop until completion or max steps.
    """
    observation = None
    
    # Reset step counter for new user inputs
    if st.session_state.step_count == 0:
        st.session_state.agent_steps = []
    
    # Main agent loop
    while True:
        # Execute a single agent step
        step_result = agent_step(user_input, observation)
        
        # Store the step
        st.session_state.agent_steps.append(step_result)
        
        # If we're done, break
        if step_result["action"] == "finish":
            # Add final response to chat history
            st.session_state.history.append({
                "role": "agent",
                "content": step_result["observation"]
            })
            st.session_state.typing = False
            break
        
        # Update for next step
        observation = step_result["observation"]
        
        # If this is the first step, add the observation to chat history
        if len(st.session_state.agent_steps) == 1:
            st.session_state.history.append({
                "role": "agent",
                "content": observation
            })
            st.session_state.typing = False
            break

# --------------------
# ---- UI COMPONENTS ----
# --------------------
def render_status_bar():
    """Render the status bar"""
    st.markdown(
        f"""
        <div class="status-bar">
            <div class="status-indicator">
                <div class="status-dot"></div>
                <span>React Agent</span>
            </div>
            <div class="status-steps">
                Step {st.session_state.step_count}/{st.session_state.max_steps}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_chat_messages():
    """Render chat message history"""
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class="user-msg-container">
                    <div class="user-msg msg">{msg['content']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="agent-msg-container">
                    <div class="agent-msg msg">{msg['content']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Typing indicator
    if st.session_state.typing:
        st.markdown(
            """
            <div class="agent-msg-container">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_thought_process():
    """Render the thought process inspector"""
    if not st.session_state.show_thoughts or not st.session_state.agent_steps:
        return
    
    st.markdown("### Agent Thought Process")
    
    for idx, step in enumerate(st.session_state.agent_steps):
        is_expanded = idx in st.session_state.expanded_thoughts
        
        # Create a unique key for this thought container
        key = f"thought_{idx}"
        
        # Render thought header
        header_html = f"""
        <div class="thought-container" id="{key}">
            <div class="thought-header" onclick="toggleThought('{key}')">
                <span>Step {idx+1}: {step.get('action', 'Unknown action')}</span>
                <span>{chevron_down}</span>
            </div>
            <div class="thought-body" id="{key}_body" {'class="expanded"' if is_expanded else ''}>
        """
        
        st.markdown(header_html, unsafe_allow_html=True)
        
        # Render thought content (only visible when expanded)
        if is_expanded:
            st.markdown(f"<div class='thought'><b>Thought:</b> {step.get('thought','')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='action'><b>Action:</b> {step.get('action','')} - <i>{step.get('action_input','')}</i></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='observation'><b>Observation:</b> {step.get('observation','')}</div>", unsafe_allow_html=True)
        
        # Close the thought body and container
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Add JavaScript to handle the toggle
    st.markdown("""
    <script>
    function toggleThought(id) {
        const body = document.getElementById(id + '_body');
        if (body.classList.contains('expanded')) {
            body.classList.remove('expanded');
        } else {
            body.classList.add('expanded');
        }
    }
    </script>
    """, unsafe_allow_html=True)

def render_input_area():
    """Render the chat input area with file upload button"""
    # Create the input container
    st.markdown(
        """
        <div class="input-container">
            <div class="input-box">
                <label for="file-upload" class="upload-btn">
                    """+plus_icon+"""
                </label>
                <input id="file-upload" class="custom-file-upload" type="file" accept="*/*" onchange="handleFileUpload(this.files)"/>
                <input id="user-input" class="input-field" type="text" placeholder="Type your message here..." onkeydown="if(event.key==='Enter') document.getElementById('send-button').click();">
                <button id="send-button" class="send-btn" onclick="sendMessage()">
                    """+send_icon+"""
                </button>
            </div>
        </div>
        
        <script>
        // Handle file upload
        function handleFileUpload(files) {
            const fileInput = document.getElementById('file-upload');
            if (files.length > 0) {
                // Show file name in the input field
                document.getElementById('user-input').value = `I've uploaded ${files[0].name}. Can you help me with this?`;
                // Submit the form with the file
                const formData = new FormData();
                formData.append('file', files[0]);
                formData.append('action', 'upload_file');
                
                // Use fetch API to upload
                fetch(window.location.href, {
                    method: 'POST',
                    body: formData
                }).then(response => {
                    console.log('File uploaded');
                    // Reset the file input
                    fileInput.value = '';
                }).catch(error => {
                    console.error('Error uploading file:', error);
                });
            }
        }
        
        // Handle sending message
        function sendMessage() {
            const userInput = document.getElementById('user-input');
            if (userInput.value.trim() !== '') {
                // Create a form to submit
                const form = document.createElement('form');
                form.method = 'POST';
                form.style.display = 'none';
                
                // Add user input field
                const inputField = document.createElement('input');
                inputField.type = 'text';
                inputField.name = 'user_input';
                inputField.value = userInput.value;
                form.appendChild(inputField);
                
                // Add action field
                const actionField = document.createElement('input');
                actionField.type = 'text';
                actionField.name = 'action';
                actionField.value = 'send_message';
                form.appendChild(actionField);
                
                // Append to body and submit
                document.body.appendChild(form);
                form.submit();
                
                // Clear input
                userInput.value = '';
            }
        }
        </script>
        """,
        unsafe_allow_html=True
    )

# --------------------
# ---- FILE HANDLING ----
# --------------------
def handle_file_upload():
    """Handle file upload from the frontend"""
    uploaded_file = st.file_uploader("Upload a file", type=None, label_visibility="collapsed", key="file_uploader")
    
    if uploaded_file is not None:
        # Check if this file is already uploaded (prevent duplicates)
        if not any(f.name == uploaded_file.name for f in st.session_state.uploaded_files):
            # Add to uploaded files list
            st.session_state.uploaded_files.append(uploaded_file)
            
            # Add system message about file upload
            file_info = f"File uploaded: {uploaded_file.name} ({len(uploaded_file.getvalue())} bytes)"
            
            # Add user message about the file
            st.session_state.history.append({
                "role": "user",
                "content": f"I've uploaded a file named {uploaded_file.name}. Can you help me with this?"
            })
            
            # Run the agent to process the file
            run_agent_loop(f"The user has uploaded a file named {uploaded_file.name}. Please acknowledge and offer assistance.")
            
            # Force a rerun to update the UI
            st.experimental_rerun()

# --------------------
# ---- AUTO INTRO ----
# --------------------
def initialize_chat():
    """Initialize the chat with an introduction message"""
    if not st.session_state.history:
        st.session_state.history.append({
            "role": "agent", 
            "content": """Hello! I'm your React Agent. I can help you with:

• General questions and conversations
• Mathematical calculations
• Generating and running Python code
• Analyzing files you upload

Just type your question or upload a file using the + button below."""
        })

# --------------------
# ---- SETTINGS ----
# --------------------
def render_settings():
    """Render agent settings in sidebar"""
    with st.sidebar:
        st.markdown("### Agent Settings")
        
        # Max steps setting
        st.session_state.max_steps = st.slider(
            "Maximum Steps", 
            min_value=5, 
            max_value=20, 
            value=st.session_state.max_steps,
            help="Maximum number of reasoning steps the agent can take"
        )
        
        # Show thoughts toggle
        st.session_state.show_thoughts = st.toggle(
            "Show Thought Process", 
            value=st.session_state.show_thoughts,
            help="Display the agent's step-by-step reasoning"
        )
        
        # Reset conversation
        if st.button("Reset Conversation"):
            st.session_state.history = []
            st.session_state.agent_steps = []
            st.session_state.step_count = 0
            st.session_state.uploaded_files = []
            st.session_state.expanded_thoughts = set()
            
            # Re-initialize chat
            initialize_chat()
            st.experimental_rerun()

# --------------------
# ---- MAIN APP ----
# --------------------
def main():
    """Main application entry point"""
    # Initialize chat if needed
    initialize_chat()
    
    # Render the status bar
    render_status_bar()
    
    # Render settings in sidebar
    render_settings()
    
    # Create columns for chat and file upload
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Render chat messages
        render_chat_messages()
        
        # Render input area (with file upload)
        render_input_area()
        
        # Handle form submission (done via JavaScript in render_input_area)
        if st.experimental_get_query_params().get("action") == ["send_message"]:
            user_input = st.experimental_get_query_params().get("user_input", [""])[0]
            
            if user_input:
                # Add user message to history
                st.session_state.history.append({
                    "role": "user",
                    "content": user_input
                })
                
                # Run agent loop
                run_agent_loop(user_input)
                
                # Rerun to update UI
                st.experimental_rerun()
    
    with col2:
        # Handle file upload (traditional Streamlit way as backup)
        handle_file_upload()
    
    # Render thought process after the chat
    render_thought_process()

# Start the app
if __name__ == "__main__":
    main()
