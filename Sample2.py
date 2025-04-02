import streamlit as st
import json
import re

# --------------------
# ---- CONFIG ----
# --------------------
st.set_page_config(page_title="React Agent - Preview #2", layout="wide")

# --------------------
# ---- STYLES ----
# --------------------
st.markdown("""
    <style>
        .chat-container { display: flex; flex-direction: column; gap: 8px; margin-bottom: 80px; }
        .user-msg { align-self: flex-end; background: #ffffff; border: 1px solid #E53935; padding: 10px; border-radius: 12px; max-width: 70%; }
        .agent-msg { align-self: flex-start; background: #FFCDD2; padding: 10px; border-radius: 12px; max-width: 70%; }
        .thought { background: #FFEBEE; padding: 8px; border-radius: 5px; margin-top:5px; }
        .action { background: #FFCDD2; padding: 8px; border-radius: 5px; margin-top:5px; }
        .observation { background: #F8BBD0; padding: 8px; border-radius: 5px; margin-top:5px; }
        .input-container { position: fixed; bottom: 0; width: 100%; background: white; padding: 10px; border-top: 1px solid #ddd; }
        .status-bar { position: sticky; top: 0; background: #FFEBEE; padding: 8px; border-bottom: 1px solid #E53935; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --------------------
# ---- SESSION STATE ----
# --------------------
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

# --------------------
# ---- BUILT-IN TOOLS ----
# --------------------
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

# --------------------
# ---- SAFE JSON PARSER ----
# --------------------
def safe_json_extract(text):
    try:
        text = text.strip()
        if "```" in text:
            text = text.split("```")[1]
        return json.loads(text)
    except:
        try:
            return json.loads(re.search(r"\{.*\}", text, re.DOTALL).group())
        except:
            return {"action": "finish"}

# --------------------
# ---- AGENT STEP ----
# --------------------
def agent_step(user_input, prev_observation=None):
    st.session_state.step_count += 1

    tool_descriptions = """
- conversation: For chatting, greeting, follow-ups, asking clarifying questions when requirements are unclear.
- calculator: For evaluating simple math expressions.
- python_executor: If on-the-fly python code needs to be generated to fulfill user's requirement, first generate the code explicitly, then execute.
- file_preview: For previewing uploaded files (e.g., first few lines).
    """

    agent_prompt = f"""[System]
You are a React Agent.
Your goal is to answer user's query using minimal steps and minimal tools.

[Current Step]: {st.session_state.step_count}
[Soft Limit]: {st.session_state.max_steps}
[Previous Observation]: {prev_observation or "None"}

[Available Tools]:
{tool_descriptions}

Always respond strictly as JSON:
{{"thought": "...", "action": "tool_name", "action_input": "..."}}
or
{{"action": "finish"}}

[User]: {user_input}
"""

    st.session_state.typing = True

    # ------------------
    # ---- LLM CALL ----
    # ------------------
    agent_response = abc_response(agent_prompt)  # <-- Inject your own LLM here

    parsed = safe_json_extract(agent_response)

    if parsed.get("action") == "finish" or st.session_state.step_count >= st.session_state.max_steps:
        st.session_state.step_count = 0
        return {"thought": "Finished.", "action": "finish", "observation": "Task completed."}

    # ------------------
    # ---- TOOL EXECUTION ----
    # ------------------
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

# --------------------
# ---- AUTO INTRO ----
# --------------------
if not st.session_state.history:
    st.session_state.history.append({"role": "agent", "content": """Hi, I'm your React Agent. Here's what I can help you with:
    
- General conversations
- Simple calculations
- Generate & run small python code
- Preview uploaded files

Please type your question or upload a file below."""})

# --------------------
# ---- UI ----
# --------------------

# ---- Status Bar ----
st.markdown(f"""
<div class="status-bar">
    <b>Status:</b> Active | Step {st.session_state.step_count}/{st.session_state.max_steps}
</div>
""", unsafe_allow_html=True)

# ---- Chat History ----
st.markdown("### Chat")
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(f"<div class='user-msg'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='agent-msg'>{msg['content']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---- Typing Indicator ----
if st.session_state.typing:
    st.markdown(f"<div class='agent-msg'>Agent is typing...</div>", unsafe_allow_html=True)
    st.session_state.typing = False

# ---- Chat Form ----
with st.form("chat_form"):
    col1, col2 = st.columns([8,1])
    with col1:
        user_input = st.text_input("Type your message")
    with col2:
        uploaded = st.file_uploader("", label_visibility="collapsed")
        if uploaded:
            st.session_state.uploaded_file = uploaded

    submitted = st.form_submit_button("Send")

if submitted and user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    step_result = agent_step(user_input)
    st.session_state.agent_steps.append(step_result)
    if step_result["action"] != "finish":
        st.session_state.history.append({"role": "agent", "content": step_result["observation"]})
    else:
        st.session_state.history.append({"role": "agent", "content": step_result["observation"]})

# ---- Thought Inspector ----
st.markdown("### Thought Process (Inspector)")
for idx, step in enumerate(st.session_state.agent_steps):
    with st.expander(f"Step {idx+1}"):
        st.markdown(f"<div class='thought'><b>Thought:</b> {step.get('thought','')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='action'><b>Action:</b> {step.get('action','')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='observation'><b>Observation:</b> {step.get('observation','')}</div>", unsafe_allow_html=True)
