import streamlit as st
import json
import re

# --- CONFIG ---
st.set_page_config(page_title="React Agent", layout="wide")

# --- STYLES ---
st.markdown("""
<style>
body {
    background-color: #fce4ec;
}
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 100px;
}
.user-msg {
    align-self: flex-end;
    background: #ffffff;
    border: 2px solid #e57373;
    color: #000;
    padding: 12px;
    border-radius: 16px 16px 0 16px;
    max-width: 70%;
}
.agent-msg {
    align-self: flex-start;
    background: #ffcdd2;
    color: #000;
    padding: 12px;
    border-radius: 16px 16px 16px 0;
    max-width: 70%;
}
.input-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: white;
    padding: 12px;
    border-top: 1px solid #ccc;
}
.status-bar {
    position: sticky;
    top: 0;
    background: #ffebee;
    padding: 10px;
    border-bottom: 1px solid #e53935;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- STATE ---
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
if "typing" not in st.session_state:
    st.session_state.typing = False
if "last_observation" not in st.session_state:
    st.session_state.last_observation = None

# --- TOOL FUNCTIONS ---
def calculator_tool(prompt):
    try:
        expr = "".join(re.findall(r"[-+*/().0-9 ]+", prompt))
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

# --- SAFE PARSER ---
def safe_json_extract(text):
    try:
        if "```" in text:
            text = text.split("```")[1]
        return json.loads(text.strip())
    except:
        try:
            return json.loads(re.search(r"\{.*\}", text, re.DOTALL).group())
        except:
            return {"action": "finish"}

# --- AGENT STEP ---
def agent_step(user_input):
    st.session_state.step_count += 1

    tools_info = """
- conversation: For chatting, greeting, follow-ups, asking user clarification.
- calculator: For simple math expressions.
- python_executor: If Python code needs to be generated for the user query, first generate clean code, then execute.
- file_preview: To show preview (e.g., first few lines) of uploaded file.
"""

    file_context = f"\n[File Uploaded]: {st.session_state.uploaded_file.name}" if st.session_state.uploaded_file else ""

    prompt = f"""[System]
You are a reasoning agent.

Your goal is to solve the user's request using the fewest reasoning steps and fewest tools possible.

[Tools Available]:
{tools_info}

[Current Step]: {st.session_state.step_count}
[Soft Step Limit]: {st.session_state.max_steps}
[Previous Observation]: {st.session_state.last_observation or "None"}{file_context}

Respond strictly as JSON:
{{"thought": "...", "action": "tool_name", "action_input": "..."}}
or
{{"action": "finish"}}

[User Message]: {user_input}
"""

    st.session_state.typing = True
    agent_raw = abc_response(prompt)  # Inject your model here
    result = safe_json_extract(agent_raw)

    if result.get("action") == "finish" or st.session_state.step_count >= st.session_state.max_steps:
        return {"thought": "Finished.", "action": "finish", "observation": "Task completed."}

    action = result.get("action")
    input_ = result.get("action_input")

    if action == "calculator":
        obs = calculator_tool(input_)
    elif action == "conversation":
        obs = conversation_tool(input_)
    elif action == "python_executor":
        obs = python_executor(input_)
    elif action == "file_preview":
        obs = file_preview()
    else:
        obs = "Unknown tool."

    st.session_state.last_observation = obs

    return {"thought": result.get("thought"), "action": action, "observation": obs}

# --- INIT INTRO ---
if not st.session_state.history:
    st.session_state.history.append({"role": "agent", "content": """
Hi! I'm your AI agent.

Here’s what I can help you with:
- General chat
- Math calculations
- Python code execution
- File inspection (after upload)

Just type your message or upload a file with the ➕ button.
"""})

# --- STATUS BAR ---
st.markdown(f"""
<div class="status-bar">
<b>Status:</b> Agent Ready | Step {st.session_state.step_count}/{st.session_state.max_steps}
</div>
""", unsafe_allow_html=True)

# --- CHAT HISTORY ---
st.markdown("### Conversation")
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for m in st.session_state.history:
    role = "user-msg" if m["role"] == "user" else "agent-msg"
    st.markdown(f"<div class='{role}'>{m['content']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- CHAT FORM ---
with st.form("chat_input"):
    col1, col2 = st.columns([9,1])
    with col1:
        user_msg = st.text_input("Your message")
    with col2:
        uploaded = st.file_uploader("➕", label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_file = uploaded
    submitted = st.form_submit_button("Send")

# --- MAIN FLOW ---
if submitted and user_msg:
    st.session_state.history.append({"role": "user", "content": user_msg})
    result = agent_step(user_msg)
    st.session_state.agent_steps.append(result)
    if result["action"] != "finish":
        st.session_state.history.append({"role": "agent", "content": result["observation"]})
    else:
        st.session_state.history.append({"role": "agent", "content": result["observation"]})

# --- THOUGHT INSPECTOR ---
st.markdown("### Thought Inspector")
for i, step in enumerate(st.session_state.agent_steps):
    with st.expander(f"Step {i+1}"):
        st.markdown(f"**Thought:** {step.get('thought', '')}")
        st.markdown(f"**Action:** {step.get('action', '')}")
        st.markdown(f"**Observation:** {step.get('observation', '')}")
