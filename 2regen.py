# --- Preview #3 | Full Production Version ---
# --- All Features Combined ---
# Before running make sure to import or define your abc_response(prompt) function

import streamlit as st
import json
import re

# --- CONFIG ---
st.set_page_config(page_title="React Agent - Full Version", layout="wide")

# --- CSS ---
st.markdown("""
<style>
body {background: #fce4ec;}
.chat-container {display: flex; flex-direction: column; gap: 10px; margin-bottom: 100px;}
.user-msg {align-self: flex-end; background: #ffffff; border: 2px solid #e57373; padding: 12px; border-radius: 16px 16px 0 16px; max-width: 70%;}
.agent-msg {align-self: flex-start; background: #ffcdd2; padding: 12px; border-radius: 16px 16px 16px 0; max-width: 70%;}
.input-bar {position: fixed; bottom: 0; left: 0; width: 100%; background: white; padding: 12px; border-top: 1px solid #ccc;}
.status-bar {position: sticky; top: 0; background: #ffebee; padding: 10px; border-bottom: 1px solid #e53935; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

# --- SESSION ---
if "history" not in st.session_state: st.session_state.history = []
if "agent_steps" not in st.session_state: st.session_state.agent_steps = []
if "step_count" not in st.session_state: st.session_state.step_count = 0
if "max_steps" not in st.session_state: st.session_state.max_steps = 10
if "uploaded_file" not in st.session_state: st.session_state.uploaded_file = None
if "typing" not in st.session_state: st.session_state.typing = False
if "last_observation" not in st.session_state: st.session_state.last_observation = None
if "tool_registry" not in st.session_state: st.session_state.tool_registry = {
    "conversation": "For chatting, greetings, clarifications",
    "calculator": "For math calculations",
    "python_executor": "For on-the-fly python code execution",
    "file_preview": "To preview uploaded files"
}

# --- TOOL FUNCTIONS ---
def calculator_tool(prompt):
    try: expr = "".join(re.findall(r"[-+*/().0-9 ]+", prompt)); result = eval(expr, {"__builtins__": None}); return f"The result is {result}"
    except: return "Invalid calculation."

def python_executor(code):
    try: exec_globals = {}; exec(code, exec_globals); return str(exec_globals.get("result", "Code executed."))
    except Exception as e: return f"Error: {str(e)}"

def file_preview():
    if st.session_state.uploaded_file:
        try: content = st.session_state.uploaded_file.getvalue().decode("utf-8").splitlines(); return "\n".join(content[:5])
        except: return "Could not read the file."
    return "No file uploaded."

def conversation_tool(prompt):
    return f"I heard you: {prompt}"

# --- SAFE PARSER ---
def safe_json_extract(text):
    try:
        if "```" in text: text = text.split("```")[1]
        return json.loads(text.strip())
    except:
        try: return json.loads(re.search(r"\{.*\}", text, re.DOTALL).group())
        except: return {"action": "finish"}

# --- AGENT STEP ---
def agent_step(user_input):
    st.session_state.step_count += 1
    tools_info = "\n".join([f"- {k}: {v}" for k,v in st.session_state.tool_registry.items()])
    file_ctx = f"\n[File Uploaded]: {st.session_state.uploaded_file.name}" if st.session_state.uploaded_file else ""
    prompt = f"""[System]\nYou are a step-limited reasoning agent.\nUse minimal steps.\nSoft Limit: {st.session_state.max_steps}\nStep: {st.session_state.step_count}\nTools:\n{tools_info}\nPrevious Observation: {st.session_state.last_observation or 'None'}{file_ctx}\n\nRespond as:\n{{\"thought\":\"...\",\"action\":\"tool_name\",\"action_input\":\"...\"}}\n\n[User]: {user_input}"""
    st.session_state.typing = True
    agent_raw = abc_response(prompt)
    result = safe_json_extract(agent_raw)
    if result.get("action") == "finish" or st.session_state.step_count >= st.session_state.max_steps:
        return {"thought": "Finished.", "action": "finish", "observation": "Task completed."}
    action, input_ = result.get("action"), result.get("action_input")
    if action == "calculator": obs = calculator_tool(input_)
    elif action == "conversation": obs = conversation_tool(input_)
    elif action == "python_executor": obs = python_executor(input_)
    elif action == "file_preview": obs = file_preview()
    elif action in st.session_state.tool_registry: obs = f"[External Tool Placeholder for {action}]"
    else: obs = "Unknown tool."
    st.session_state.last_observation = obs
    return {"thought": result.get("thought"), "action": action, "observation": obs}

# --- INTRO ---
if not st.session_state.history:
    st.session_state.history.append({"role": "agent", "content": "Hi! I'm your React Agent.\n\nI can:\n- Chat\n- Calculate\n- Execute Python\n- Preview Files\n- Create & Test new Tools\nUse the input below or upload a file."})

# --- STATUS BAR ---
st.markdown(f"<div class=\"status-bar\"><b>Status:</b> Agent Ready | Step {st.session_state.step_count}/{st.session_state.max_steps}</div>", unsafe_allow_html=True)

# --- CHAT ---
st.markdown("### Conversation")
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for m in st.session_state.history:
    role = "user-msg" if m["role"] == "user" else "agent-msg"
    st.markdown(f"<div class='{role}'>{m['content']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- INPUT ---
with st.form("chat_input"):
    col1, col2 = st.columns([9,1])
    with col1: user_msg = st.text_input("Your message")
    with col2: uploaded = st.file_uploader("➕", label_visibility="collapsed");
    if uploaded: st.session_state.uploaded_file = uploaded
    submitted = st.form_submit_button("Send")

# --- MAIN LOOP ---
if submitted and user_msg:
    st.session_state.history.append({"role": "user", "content": user_msg})
    result = agent_step(user_msg)
    st.session_state.agent_steps.append(result)
    st.session_state.history.append({"role": "agent", "content": result["observation"]})

# --- INSPECTOR ---
st.markdown("### Thought Inspector")
for i, step in enumerate(st.session_state.agent_steps):
    with st.expander(f"Step {i+1}"):
        st.markdown(f"**Thought:** {step.get('thought', '')}")
        st.markdown(f"**Action:** {step.get('action', '')}")
        st.markdown(f"**Observation:** {step.get('observation', '')}")
