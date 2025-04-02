# --- React Agent Core (Preview #1) ---
import streamlit as st
import json
import re

# ---- Streamlit Config ----
st.set_page_config(page_title="React Agent", layout="wide")

# ---- CSS ----
st.markdown("""
    <style>
        .user-msg {background: #FFEBEE; padding: 10px; border-radius: 10px; margin-bottom:5px; width: fit-content; align-self: flex-end;}
        .agent-msg {background: #FFCDD2; padding: 10px; border-radius: 10px; margin-bottom:5px; width: fit-content;}
        .thought {background: #FFEBEE; padding: 8px; border-radius: 5px; margin-top:5px;}
        .action {background: #FFCDD2; padding: 8px; border-radius: 5px; margin-top:5px;}
        .observation {background: #F8BBD0; padding: 8px; border-radius: 5px; margin-top:5px;}
        .chat-container {display: flex; flex-direction: column;}
        .input-container {position: fixed; bottom: 0; width: 100%; background: white; padding: 10px;}
    </style>
""", unsafe_allow_html=True)

# ---- Session ----
if "history" not in st.session_state:
    st.session_state.history = []
if "agent_steps" not in st.session_state:
    st.session_state.agent_steps = []
if "step_count" not in st.session_state:
    st.session_state.step_count = 0
if "max_steps" not in st.session_state:
    st.session_state.max_steps = 10
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

# ---- Built-in Tools ----
def calculator_tool(prompt):
    try:
        expr = re.findall(r"[-+*/().0-9 ]+", prompt)
        expr = "".join(expr)
        result = eval(expr, {"__builtins__": None})
        return f"The result is {result}"
    except:
        return "Invalid calculation."

def python_executor(code):
    try:
        exec_globals = {}
        exec(code, exec_globals)
        return str(exec_globals.get("result", "Code executed."))
    except Exception as e:
        return f"Error: {str(e)}"

def file_preview():
    if st.session_state.uploaded_file:
        try:
            content = st.session_state.uploaded_file.getvalue().decode("utf-8").splitlines()
            return "\n".join(content[:5])
        except:
            return "Could not read the file."
    return "No file uploaded."

def conversation_tool(prompt):
    return f"I heard you: {prompt}"

# ---- Agent Controller ----
def agent_step(user_input, prev_observation=None):
    st.session_state.step_count += 1

    # ---- Prompt ----
    agent_prompt = f"""[System]
You are a React Agent.

Your job is to solve the user's query using minimum steps and tools.

Available tools:
- calculator
- conversation
- python_executor
- file_preview

Soft Step Limit = {st.session_state.max_steps}
Steps used so far = {st.session_state.step_count}
Current observation = {prev_observation or "None"}

Respond strictly in:
{{"thought": "...", "action": "tool_name", "action_input": "..."}}
or
{{"action": "finish"}}

[User]: {user_input}
"""

    # ---- LLM Call ----
    agent_response = abc_response(agent_prompt)  # <-- you will import this yourself
    try:
        parsed = json.loads(agent_response)
    except:
        parsed = {"action": "finish"}

    # ---- React Loop ----
    if parsed.get("action") == "finish" or st.session_state.step_count >= st.session_state.max_steps:
        st.session_state.step_count = 0  # Reset step count
        return {"thought": "Finished.", "action": "finish", "observation": "Task completed."}

    # ---- Tool Dispatcher ----
    tool_name = parsed.get("action")
    action_input = parsed.get("action_input")

    if tool_name == "calculator":
        observation = calculator_tool(action_input)
    elif tool_name == "conversation":
        observation = conversation_tool(action_input)
    elif tool_name == "python_executor":
        observation = python_executor(action_input)
    elif tool_name == "file_preview":
        observation = file_preview()
    else:
        observation = "Unknown tool requested."

    return {"thought": parsed.get("thought", ""), "action": tool_name, "action_input": action_input, "observation": observation}

# ---- Agent Auto-Intro ----
if not st.session_state.history:
    st.session_state.history.append({"role": "agent", "content": """Hi, I'm your React Agent. Here's what I can help you with:

- Simple conversations
- Basic calculations
- Run small Python code
- File uploads (CSV/JSON) for preview
- I will always try to answer you in the minimum steps.

You can also upload a file using the [+] button."""})

# ---- UI ----
st.title("React Agent - Preview #1")

uploaded = st.file_uploader("Upload file", type=None)
if uploaded:
    st.session_state.uploaded_file = uploaded

# ---- Chat Form ----
with st.form("chat_form"):
    user_input = st.text_input("Type your message...")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.history.append({"role": "user", "content": user_input})

    # Agent Thinks
    step_result = agent_step(user_input)
    st.session_state.agent_steps.append(step_result)

    # Agent Replies
    if step_result["action"] != "finish":
        st.session_state.history.append({"role": "agent", "content": step_result["observation"]})
    else:
        st.session_state.history.append({"role": "agent", "content": step_result["observation"]})

# ---- Chat History ----
st.markdown("### Chat")
with st.container():
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(f"<div class='user-msg'>You: {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='agent-msg'>Agent: {msg['content']}</div>", unsafe_allow_html=True)

# ---- Thought Process ----
st.markdown("### Thought Process")
for idx, step in enumerate(st.session_state.agent_steps):
    with st.expander(f"Step {idx+1}"):
        st.markdown(f"<div class='thought'><b>Thought:</b> {step.get('thought','')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='action'><b>Action:</b> {step.get('action','')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='observation'><b>Observation:</b> {step.get('observation','')}</div>", unsafe_allow_html=True)
