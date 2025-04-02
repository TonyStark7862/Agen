import streamlit as st
import json
import re
import uuid
import time
from datetime import datetime
import os
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd

# --------------------
# ---- CONFIG ----
# --------------------
st.set_page_config(
    page_title="ReAct Agent",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------
# ---- STYLES ----
# --------------------
def load_css():
    """Load custom CSS styles for the app"""
    st.markdown("""
    <style>
        /* Global styles */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
        
        /* Main container */
        .main {
            background-color: #f5f5f5;
        }
        
        /* Chat container */
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 16px;
            padding-bottom: 100px;
            max-width: 800px;
            margin: 0 auto;
        }
        
        /* Message bubbles */
        .message {
            display: flex;
            margin-bottom: 10px;
        }
        
        .user-message {
            justify-content: flex-end;
        }
        
        .agent-message {
            justify-content: flex-start;
        }
        
        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 10px;
            margin-top: 2px;
            flex-shrink: 0;
        }
        
        .user-avatar {
            background-color: #E53935;
            color: white;
            margin-left: 10px;
            margin-right: 0;
            order: 1;
        }
        
        .agent-avatar {
            background-color: #f0f0f0;
            color: #E53935;
        }
        
        .message-content {
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 70%;
            line-height: 1.5;
            position: relative;
        }
        
        .user-content {
            background-color: #E53935;
            color: white;
            border-radius: 18px 18px 0 18px;
        }
        
        .agent-content {
            background-color: white;
            color: #333;
            border-radius: 18px 18px 18px 0;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        
        /* Typing indicator */
        .typing-indicator {
            display: flex;
            padding: 14px 18px;
            background: white;
            border-radius: 18px 18px 18px 0;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            width: fit-content;
            position: relative;
        }
        
        .typing-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #E53935;
            margin-right: 4px;
            animation: typing-bounce 1.4s infinite;
            opacity: 0.7;
        }
        
        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
            margin-right: 0;
        }
        
        @keyframes typing-bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-4px); }
        }
        
        /* Header and Input area */
        .header {
            position: sticky;
            top: 0;
            background-color: white;
            border-bottom: 1px solid #eee;
            padding: 16px 20px;
            z-index: 100;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header-title {
            font-weight: 600;
            font-size: 16px;
            color: #333;
            display: flex;
            align-items: center;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #4CAF50;
            margin-right: 8px;
        }
        
        .header-info {
            font-size: 14px;
            color: #666;
            background: #f5f5f5;
            padding: 4px 10px;
            border-radius: 12px;
        }
        
        .input-area {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            padding: 16px;
            border-top: 1px solid #eee;
            z-index: 100;
        }
        
        .input-container {
            max-width: 800px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            background: #f5f5f5;
            border-radius: 24px;
            padding: 6px 8px;
        }
        
        /* Thought process */
        .thought-process {
            margin-top: 40px;
            margin-bottom: 80px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .thought-title {
            font-weight: 600;
            font-size: 18px;
            color: #333;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
        }
        
        .thought-icon {
            margin-right: 8px;
            color: #E53935;
        }
        
        .thought-container {
            background: white;
            border-radius: 8px;
            margin-bottom: 12px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .thought-step {
            background: #f9f9f9;
            padding: 12px 16px;
            border-bottom: 1px solid #eee;
        }
        
        .thought-header {
            font-weight: 500;
            margin-bottom: 4px;
            color: #E53935;
        }
        
        .thought-content {
            white-space: pre-wrap;
            overflow-x: auto;
        }
        
        .action-content, .observation-content {
            padding: 8px;
            background: #f5f5f5;
            border-radius: 4px;
            margin-top: 8px;
            white-space: pre-wrap;
            overflow-x: auto;
        }
        
        /* File upload preview */
        .file-preview {
            background: white;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .file-header {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .file-icon {
            margin-right: 12px;
            background: #E5F0FF;
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #2563EB;
        }
        
        .file-name {
            font-weight: 500;
            font-size: 14px;
        }
        
        .file-meta {
            font-size: 12px;
            color: #666;
        }
        
        .file-content {
            background: #f9f9f9;
            border-radius: 4px;
            padding: 8px;
            font-family: monospace;
            font-size: 12px;
            white-space: pre-wrap;
            overflow-x: auto;
            max-height: 200px;
            overflow-y: auto;
        }
        
        /* Tool usage pills */
        .tool-pill {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-right: 4px;
            margin-bottom: 4px;
            background: #F3F4F6;
            color: #333;
            font-weight: 500;
        }
        
        /* Settings sidebar */
        .sidebar .block-container {
            padding-top: 2rem;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .message-content {
                max-width: 90%;
            }
        }
        
        /* Expandable sections */
        .expander-head {
            cursor: pointer;
            user-select: none;
        }
        
        .expander-icon {
            display: inline-block;
            transition: transform 0.3s;
        }
        
        .expanded .expander-icon {
            transform: rotate(90deg);
        }
        
        /* Custom file uploader button */
        .custom-uploader .stFileUploader {
            width: auto !important;
        }
        
        .custom-uploader .stFileUploader > div {
            padding: 0 !important;
        }
        
        .custom-uploader .stFileUploader > div > div {
            padding: 0 !important;
        }
        
        .custom-uploader .stFileUploader > div > div > button {
            background: #f5f5f5 !important;
            border: none !important;
            border-radius: 50% !important;
            width: 40px !important;
            height: 40px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: #666 !important;
        }
        
        .custom-uploader .stFileUploader > div > div > button > p {
            display: none;
        }
        
        .custom-uploader .stFileUploader > div > div > button::before {
            content: "+" !important;
            font-size: 24px !important;
            font-weight: 400 !important;
        }
        
        .custom-uploader .stFileUploader > div > small {
            display: none !important;
        }
        
        /* Custom file uploader and message input layout */
        .stHorizontal > div:first-child {
            flex: 0 0 40px !important;
        }
        
        .stHorizontal > div:last-child {
            flex: 0 0 60px !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --------------------
# ---- ICONS ----
# --------------------
def icon(name, color="#333333", size=24):
    """Get SVG icon as HTML"""
    icons = {
        "send": f'<span>➤</span>',
        "file": f'<span>📄</span>',
        "user": f'<span>👤</span>',
        "bot": f'<span>🤖</span>',
        "thought": f'<span>💭</span>',
        "reload": f'<span>🔄</span>',
        "settings": f'<span>⚙️</span>',
        "chevron": f'<span>▶</span>'
    }
    return icons.get(name, "")

# --------------------
# ---- SESSION STATE ----
# --------------------
def init_session_state():
    """Initialize session state variables"""
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
    
    if "show_thoughts" not in st.session_state:
        st.session_state.show_thoughts = True
    
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    
    if "intro_done" not in st.session_state:
        st.session_state.intro_done = False

# --------------------
# ---- TOOLS ----
# --------------------
class Tool:
    """Base class for agent tools"""
    
    def __init__(self, name: str, description: str, examples: List[str] = None):
        self.name = name
        self.description = description
        self.examples = examples or []
    
    def execute(self, action_input: str) -> str:
        """Execute the tool with the given input"""
        raise NotImplementedError("Tool must implement execute method")

class CalculatorTool(Tool):
    """Tool for evaluating mathematical expressions"""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Evaluate mathematical expressions",
            examples=["2 + 2", "5 * (3 + 2)", "sqrt(16)", "sin(0.5)"]
        )
    
    def execute(self, action_input: str) -> str:
        try:
            # Safely evaluate mathematical expressions
            # First clean the input to only allow safe math operations
            clean_expr = re.sub(r'[^0-9+\-*/().^\s]', '', action_input)
            
            # Replace ^ with ** for exponentiation
            clean_expr = clean_expr.replace('^', '**')
            
            # Create a safe local namespace with math functions
            import math
            safe_locals = {
                'abs': abs,
                'round': round,
                'max': max,
                'min': min,
                'sum': sum,
                'pow': pow,
                # Math module functions
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'asin': math.asin,
                'acos': math.acos,
                'atan': math.atan,
                'log': math.log,
                'log10': math.log10,
                'exp': math.exp,
                'pi': math.pi,
                'e': math.e
            }
            
            # Evaluate the expression
            result = eval(clean_expr, {"__builtins__": {}}, safe_locals)
            
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

class ConversationTool(Tool):
    """Tool for general conversation with the user"""
    
    def __init__(self):
        super().__init__(
            name="conversation",
            description="For general conversation, follow-ups, asking clarifying questions",
            examples=["Hello, how can I help you?", "Could you clarify what you mean by that?"]
        )
    
    def execute(self, action_input: str) -> str:
        return action_input

class PythonExecutorTool(Tool):
    """Tool for executing Python code"""
    
    def __init__(self):
        super().__init__(
            name="python_executor",
            description="Generate and execute Python code to solve problems",
            examples=["print('Hello, world!')", "result = sum([1, 2, 3, 4, 5])"]
        )
    
    def execute(self, action_input: str) -> str:
        try:
            # Prepare a safe execution environment
            exec_globals = {
                "print": lambda *args, **kwargs: None,  # No-op print function
                "input": lambda *args, **kwargs: "",    # No-op input function
                "open": lambda *args, **kwargs: None,   # No-op open function
                "__import__": lambda *args, **kwargs: None,  # No-op import
            }
            
            # Create a string buffer to capture print output
            from io import StringIO
            import sys
            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()
            
            try:
                # Execute the code in a safe environment
                exec_globals["__builtins__"] = {"__name__": "__main__", "range": range, "len": len}
                
                # Add safe builtins
                for safe_builtin in ["abs", "all", "any", "bool", "dict", "enumerate", "filter", 
                                     "float", "int", "len", "list", "map", "max", "min", "range", 
                                     "round", "set", "sorted", "str", "sum", "tuple", "zip"]:
                    exec_globals["__builtins__"][safe_builtin] = __builtins__[safe_builtin]
                
                # Add numpy and pandas if available
                try:
                    import numpy as np
                    import pandas as pd
                    exec_globals["np"] = np
                    exec_globals["pd"] = pd
                except ImportError:
                    pass
                
                # Execute code
                exec(action_input, exec_globals)
                
                # Get output
                output = mystdout.getvalue()
                
                # Check if 'result' variable was set
                if "result" in exec_globals:
                    if output:
                        return f"{output}\n\nResult: {exec_globals['result']}"
                    else:
                        return f"Result: {exec_globals['result']}"
                else:
                    return output if output else "Code executed successfully, but no output was generated."
            
            finally:
                # Restore stdout
                sys.stdout = old_stdout
        except Exception as e:
            return f"Error executing Python code: {str(e)}"

class FilePreviewTool(Tool):
    """Tool for previewing uploaded files"""
    
    def __init__(self):
        super().__init__(
            name="file_preview",
            description="Preview contents of uploaded files",
            examples=["preview file.csv", "show first 10 lines of data.txt"]
        )
    
    def execute(self, action_input: str) -> str:
        if not st.session_state.uploaded_files:
            return "No files have been uploaded. Please upload a file first."
        
        # If a specific file is requested by name
        if action_input.strip():
            file_name = action_input.lower().strip()
            
            # Check if the exact file name is mentioned
            for file in st.session_state.uploaded_files:
                if file.name.lower() == file_name or file_name in file.name.lower():
                    return self._preview_file(file)
            
            # If we got here, the file wasn't found
            available_files = ", ".join([f.name for f in st.session_state.uploaded_files])
            return f"File '{action_input}' not found. Available files: {available_files}"
        
        # If no specific file is requested, preview the most recently uploaded file
        return self._preview_file(st.session_state.uploaded_files[-1])
    
    def _preview_file(self, file) -> str:
        """Generate a preview of the file contents"""
        try:
            # Get file extension
            file_ext = os.path.splitext(file.name)[1].lower()
            
            # Handle different file types
            if file_ext in ['.csv', '.tsv']:
                try:
                    # Try to read as a CSV
                    df = pd.read_csv(file)
                    preview = f"File: {file.name}\nSize: {len(file.getvalue())} bytes\nRows: {len(df)}, Columns: {len(df.columns)}\n"
                    preview += f"Columns: {', '.join(df.columns.tolist())}\n\n"
                    preview += df.head(5).to_string()
                    return preview
                except Exception as e:
                    # Fall back to text preview if pandas fails
                    content = file.getvalue().decode("utf-8", errors="replace").splitlines()
                    preview = "\n".join(content[:10])
                    return f"File: {file.name}\nSize: {len(file.getvalue())} bytes\nPreview (first 10 lines):\n{preview}\n...(truncated)"
            
            elif file_ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json']:
                # Read as text
                content = file.getvalue().decode("utf-8", errors="replace").splitlines()
                preview = "\n".join(content[:20])
                return f"File: {file.name}\nSize: {len(file.getvalue())} bytes\nPreview (first 20 lines):\n{preview}\n...(truncated)"
            
            elif file_ext in ['.xlsx', '.xls']:
                try:
                    # Try to read as Excel
                    df = pd.read_excel(file)
                    preview = f"File: {file.name}\nSize: {len(file.getvalue())} bytes\nRows: {len(df)}, Columns: {len(df.columns)}\n"
                    preview += f"Columns: {', '.join(df.columns.tolist())}\n\n"
                    preview += df.head(5).to_string()
                    return preview
                except Exception as e:
                    return f"File: {file.name}\nSize: {len(file.getvalue())} bytes\nType: Excel file (preview not available)\nError: {str(e)}"
            
            elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                return f"File: {file.name}\nSize: {len(file.getvalue())} bytes\nType: Image file (visual preview not available)"
            
            elif file_ext in ['.pdf']:
                return f"File: {file.name}\nSize: {len(file.getvalue())} bytes\nType: PDF document (preview not available)"
            
            else:
                # Generic binary file
                return f"File: {file.name}\nSize: {len(file.getvalue())} bytes\nType: Binary file (preview not available)"
                
        except Exception as e:
            return f"Error previewing file {file.name}: {str(e)}"

class ListFilesTool(Tool):
    """Tool for listing all uploaded files"""
    
    def __init__(self):
        super().__init__(
            name="list_files",
            description="List all uploaded files",
            examples=["list files", "show uploaded files"]
        )
    
    def execute(self, action_input: str) -> str:
        if not st.session_state.uploaded_files:
            return "No files have been uploaded."
        
        file_list = []
        for idx, file in enumerate(st.session_state.uploaded_files):
            file_size = len(file.getvalue())
            file_list.append(f"{idx+1}. {file.name} ({self._format_bytes(file_size)})")
        
        return "Uploaded files:\n" + "\n".join(file_list)
    
    def _format_bytes(self, size: int) -> str:
        """Format byte size to human readable format"""
        power = 2**10
        n = 0
        labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
        while size > power:
            size /= power
            n += 1
        return f"{size:.1f} {labels[n]}"

class AnalyzeFileTool(Tool):
    """Tool for analyzing file contents"""
    
    def __init__(self):
        super().__init__(
            name="analyze_file",
            description="Analyze content of an uploaded file",
            examples=["analyze data.csv", "provide statistics for sales.xlsx"]
        )
    
    def execute(self, action_input: str) -> str:
        if not st.session_state.uploaded_files:
            return "No files have been uploaded. Please upload a file first."
        
        # Try to find the specified file
        target_file = None
        file_name = action_input.strip().lower()
        
        if file_name:
            for file in st.session_state.uploaded_files:
                if file.name.lower() == file_name or file_name in file.name.lower():
                    target_file = file
                    break
            
            if not target_file:
                available_files = ", ".join([f.name for f in st.session_state.uploaded_files])
                return f"File '{action_input}' not found. Available files: {available_files}"
        else:
            # Use the most recently uploaded file if none specified
            target_file = st.session_state.uploaded_files[-1]
        
        # Analyze the file based on its type
        file_ext = os.path.splitext(target_file.name)[1].lower()
        
        # CSV/TSV analysis
        if file_ext in ['.csv', '.tsv']:
            try:
                df = pd.read_csv(target_file)
                analysis = self._analyze_dataframe(df, target_file.name)
                return analysis
            except Exception as e:
                return f"Error analyzing CSV file: {str(e)}"
        
        # Excel analysis
        elif file_ext in ['.xlsx', '.xls']:
            try:
                df = pd.read_excel(target_file)
                analysis = self._analyze_dataframe(df, target_file.name)
                return analysis
            except Exception as e:
                return f"Error analyzing Excel file: {str(e)}"
        
        # Text file analysis
        elif file_ext in ['.txt', '.md', '.py', '.js', '.html', '.css']:
            try:
                content = target_file.getvalue().decode("utf-8", errors="replace")
                lines = content.splitlines()
                
                analysis = f"Text file analysis: {target_file.name}\n"
                analysis += f"Total lines: {len(lines)}\n"
                analysis += f"Total characters: {len(content)}\n"
                analysis += f"Words: {len(content.split())}\n\n"
                
                # Most common words
                if len(content) > 0:
                    words = re.findall(r'\b\w+\b', content.lower())
                    word_freq = {}
                    for word in words:
                        if len(word) > 2:  # Ignore short words
                            word_freq[word] = word_freq.get(word, 0) + 1
                    
                    # Get top 10 words
                    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
                    if top_words:
                        analysis += "Most common words:\n"
                        for word, count in top_words:
                            analysis += f"- {word}: {count} occurrences\n"
                
                return analysis
            except Exception as e:
                return f"Error analyzing text file: {str(e)}"
        
        # JSON analysis
        elif file_ext in ['.json']:
            try:
                content = target_file.getvalue().decode("utf-8", errors="replace")
                import json
                data = json.loads(content)
                
                analysis = f"JSON file analysis: {target_file.name}\n"
                
                if isinstance(data, list):
                    analysis += f"JSON contains a list with {len(data)} items\n"
                    if len(data) > 0 and isinstance(data[0], dict):
                        # Sample structure of first item
                        analysis += f"First item keys: {', '.join(data[0].keys())}\n"
                elif isinstance(data, dict):
                    analysis += f"JSON contains an object with {len(data)} keys\n"
                    analysis += f"Top-level keys: {', '.join(list(data.keys())[:10])}"
                    if len(data.keys()) > 10:
                        analysis += " (and more...)"
                
                return analysis
            except Exception as e:
                return f"Error analyzing JSON file: {str(e)}"
        
        else:
            return f"File type analysis not supported for {target_file.name}"
    
    def _analyze_dataframe(self, df, file_name):
        """Generate statistics for a pandas DataFrame"""
        analysis = f"Data analysis for {file_name}:\n\n"
        
        # Basic info
        analysis += f"Rows: {len(df)}, Columns: {len(df.columns)}\n"
        analysis += f"Columns: {', '.join(df.columns.tolist())}\n\n"
        
        # Data types
        analysis += "Column data types:\n"
        for col, dtype in df.dtypes.items():
            analysis += f"- {col}: {dtype}\n"
        analysis += "\n"
        
        # Numeric columns statistics
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            analysis += "Numeric columns statistics:\n"
            for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
                stats = df[col].describe()
                analysis += f"- {col}:\n"
                analysis += f"  Mean: {stats['mean']:.2f}\n"
                analysis += f"  Min: {stats['min']:.2f}\n"
                analysis += f"  Max: {stats['max']:.2f}\n"
                analysis += f"  Std Dev: {stats['std']:.2f}\n"
            
            if len(numeric_cols) > 5:
                analysis += f"(Statistics for {len(numeric_cols) - 5} more numeric columns not shown)\n"
            
            analysis += "\n"
        
        # Missing values
        missing_values = df.isnull().sum()
        if missing_values.sum() > 0:
            analysis += "Missing values by column:\n"
            for col, count in missing_values.items():
                if count > 0:
                    percentage = (count / len(df)) * 100
                    analysis += f"- {col}: {count} ({percentage:.1f}%)\n"
            analysis += "\n"
        else:
            analysis += "No missing values found in the dataset.\n\n"
        
        # Sample data
        analysis += "Sample data (first 5 rows):\n"
        analysis += df.head(5).to_string()
        
        return analysis

# --------------------
# ---- TOOL REGISTRY ----
# --------------------
def get_tools() -> Dict[str, Tool]:
    """Get all available tools"""
    return {
        "calculator": CalculatorTool(),
        "conversation": ConversationTool(),
        "python_executor": PythonExecutorTool(),
        "file_preview": FilePreviewTool(),
        "list_files": ListFilesTool(),
        "analyze_file": AnalyzeFileTool()
    }

# --------------------
# ---- REACT AGENT ----
# --------------------
class ReactAgent:
    """ReAct Agent implementation"""
    
    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps
        self.tools = get_tools()
        self.current_step = 0
        self.steps_history = []
    
    def reset(self):
        """Reset agent state"""
        self.current_step = 0
        self.steps_history = []
    
    def _format_tool_descriptions(self) -> str:
        """Format tool descriptions for the prompt"""
        descriptions = []
        for tool_name, tool in self.tools.items():
            examples_str = ""
            if tool.examples:
                examples_str = f" Examples: {', '.join(f'`{e}`' for e in tool.examples[:2])}"
            descriptions.append(f"- {tool.name}: {tool.description}.{examples_str}")
        
        return "\n".join(descriptions)
    
    def _format_previous_steps(self) -> str:
        """Format previous steps for the prompt"""
        if not self.steps_history:
            return "None"
        
        # Include only the most recent step
        last_step = self.steps_history[-1]
        
        result = (
            f"Tool: {last_step['action']}\n"
            f"Input: {last_step['action_input']}\n"
            f"Observation: {last_step['observation']}\n"
        )
        
        # Add error info if present
        if last_step.get('error'):
            result += f"Error: {last_step['error']}\n"
        
        return result
    
    def _should_use_file_tools(self) -> bool:
        """Check if file-related tools should be used based on context"""
        return len(st.session_state.uploaded_files) > 0
    
    def _build_prompt(self, user_query: str) -> str:
        """Build the prompt for the agent"""
        tool_descriptions = self._format_tool_descriptions()
        previous_steps = self._format_previous_steps()
        
        prompt = f"""[System]
You are a ReAct Agent that follows the "Thought-Action-Observation" pattern to solve tasks.
Your goal is to answer the user's question using the minimum number of steps and tools necessary.

[Current Step]: {self.current_step + 1}
[Step Limit]: {self.max_steps} (Try to complete the task in fewer steps where possible)
[Previous Step]: {previous_steps}

[Available Tools]:
{tool_descriptions}

[Instructions]:
1. First, carefully plan how to solve the user's task step by step.
2. Always use the most appropriate tool for the task.
3. For file-related tasks, first check what files are available using the list_files tool.
4. Be efficient and try to minimize the number of steps needed.
5. If you encounter an error, try a different approach.
6. When you've fully answered the user's query, finish the conversation.

[Response Format]
Respond with a JSON object containing:
- "thought": Your detailed reasoning about what to do next (required)
- "action": The name of the tool to use (required)
- "action_input": Input for the selected tool (required)

Example response:
```json
{{
  "thought": "I need to calculate 25 × 4 to answer this question",
  "action": "calculator",
  "action_input": "25 * 4"
}}
```

To finish the conversation, respond with:
```json
{{
  "thought": "I've completed the task and provided a full answer",
  "action": "finish",
  "action_input": "Final response to the user"
}}
```

[User Query]: {user_query}
"""
        return prompt
    
    def _parse_response(self, response: str) -> Dict[str, str]:
        """Parse the LLM response into structured data"""
        try:
            # Try to find JSON data in the response
            # First check for code blocks
            json_pattern = r"```(?:json)?\s*([\s\S]*?)```"
            match = re.search(json_pattern, response)
            
            if match:
                # Found JSON in code block
                json_str = match.group(1).strip()
                return json.loads(json_str)
            
            # If no code block, try to find JSON object directly
            json_pattern = r"\{[\s\S]*\}"
            match = re.search(json_pattern, response)
            
            if match:
                json_str = match.group(0).strip()
                return json.loads(json_str)
            
            # If still no JSON found, try to convert the entire response
            return json.loads(response.strip())
            
        except Exception as e:
            # Fallback for parsing errors
            print(f"Error parsing response: {e}")
            
            # Try to extract thought, action, and action_input directly
            thought_match = re.search(r'"thought"\s*:\s*"([^"]*)"', response)
            action_match = re.search(r'"action"\s*:\s*"([^"]*)"', response)
            action_input_match = re.search(r'"action_input"\s*:\s*"([^"]*)"', response)
            
            thought = thought_match.group(1) if thought_match else "Couldn't determine next step clearly."
            action = action_match.group(1) if action_match else "conversation"
            action_input = action_input_match.group(1) if action_input_match else "I encountered an error understanding your request. Could you please clarify what you need help with?"
            
            return {
                "thought": thought,
                "action": action,
                "action_input": action_input
            }
    
    def execute_step(self, user_query: str) -> Dict[str, str]:
        """Execute a single step of the ReAct agent"""
        # Check if we've reached the maximum number of steps
        if self.current_step >= self.max_steps:
            return {
                "thought": "I've reached the maximum number of steps allowed.",
                "action": "finish",
                "action_input": "I've reached my step limit. Here's what I've determined so far: " + 
                               (self.steps_history[-1]["observation"] if self.steps_history else "Unable to complete the task within step limit."),
                "observation": "Maximum steps reached."
            }
        
        # Build the prompt for the LLM
        prompt = self._build_prompt(user_query)
        
        # Call the LLM (placeholder for actual implementation)
        llm_response = self._call_llm(prompt)
        
        # Parse the response
        parsed_response = self._parse_response(llm_response)
        
        # Extract components
        thought = parsed_response.get("thought", "")
        action = parsed_response.get("action", "conversation")
        action_input = parsed_response.get("action_input", "")
        
        # Check if we should finish
        if action.lower() == "finish":
            step_result = {
                "thought": thought,
                "action": "finish",
                "action_input": action_input,
                "observation": action_input
            }
            self.steps_history.append(step_result)
            return step_result
        
        # Execute the selected tool
        observation = "Tool not found."
        error = None
        
        try:
            if action in self.tools:
                observation = self.tools[action].execute(action_input)
            else:
                # If tool not found, use conversation tool as fallback
                observation = f"Tool '{action}' not found. Available tools: {', '.join(self.tools.keys())}"
                error = f"Invalid tool: {action}"
        except Exception as e:
            observation = f"Error executing tool {action}: {str(e)}"
            error = str(e)
        
        # Record the step
        step_result = {
            "thought": thought,
            "action": action,
            "action_input": action_input,
            "observation": observation
        }
        
        if error:
            step_result["error"] = error
        
        self.steps_history.append(step_result)
        self.current_step += 1
        
        return step_result
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt (placeholder implementation)"""
        # This is a placeholder for the actual LLM call
        # In a real implementation, this would call an external API like GPT-4
        
        # For demonstration purposes, we'll just return a simple JSON response
        # This would be replaced with your actual LLM integration (e.g., OpenAI, Claude, etc.)
        return abc_response(prompt)

def abc_response(prompt: str) -> str:
    """Placeholder for actual LLM implementation"""
    # This would be replaced with your actual LLM call
    # For demonstration purposes, returning a dummy response
    return """```json
{
  "thought": "I should greet the user and ask how I can help",
  "action": "conversation",
  "action_input": "Hello! I'm your ReAct Agent assistant. How can I help you today?"
}
```"""

# --------------------
# ---- UI COMPONENTS ----
# --------------------
def render_header():
    """Render the header with title and status"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(
            """
            <div class="header-title">
                <div class="status-dot"></div>
                ReAct Agent
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="header-info">
                Step {st.session_state.step_count}/{st.session_state.max_steps}
            </div>
            """,
            unsafe_allow_html=True
        )

def render_message(message):
    """Render a chat message"""
    if message["role"] == "user":
        st.markdown(
            f"""
            <div class="message user-message">
                <div class="message-content user-content">{message['content']}</div>
                <div class="avatar user-avatar">👤</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="message agent-message">
                <div class="avatar agent-avatar">🤖</div>
                <div class="message-content agent-content">{message['content']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_typing_indicator():
    """Render typing indicator"""
    st.markdown(
        """
        <div class="message agent-message">
            <div class="avatar agent-avatar">🤖</div>
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_chat_messages():
    """Render all chat messages"""
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Render all messages
        for message in st.session_state.history:
            render_message(message)
        
        # Show typing indicator if agent is processing
        if st.session_state.typing:
            render_typing_indicator()
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_thought_process():
    """Render the agent's thought process"""
    if not st.session_state.show_thoughts or not st.session_state.agent_steps:
        return
    
    st.markdown(
        f"""
        <div class="thought-process">
            <div class="thought-title">
                <span class="thought-icon">💭</span>
                Agent Thought Process
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    for idx, step in enumerate(st.session_state.agent_steps):
        with st.expander(f"Step {idx+1}: {step.get('action', 'Unknown')}"):
            st.markdown(f"**Thought:** {step.get('thought', '')}")
            st.markdown(f"**Action:** {step.get('action', '')}")
            st.markdown(f"**Action Input:** {step.get('action_input', '')}")
            
            # Format observation with code styling if it looks like code
            observation = step.get('observation', '')
            if '```' in observation or observation.strip().startswith('def ') or observation.strip().startswith('import '):
                st.code(observation)
            else:
                st.markdown(f"**Observation:** {observation}")
            
            # Show error if present
            if 'error' in step:
                st.error(f"Error: {step['error']}")

def render_input_area():
    """Render the chat input area with file upload"""
    st.markdown('<div class="input-area">', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        
        # Create columns for upload button, input field, and send button
        cols = st.columns([1, 10, 1])
        
        with cols[0]:
            # File upload button (styled as a plus icon)
            st.markdown('<div class="custom-uploader">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader("", label_visibility="collapsed", key="file_uploader")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if uploaded_file:
                # Add to uploaded files list if not already present
                if not any(f.name == uploaded_file.name for f in st.session_state.uploaded_files):
                    st.session_state.uploaded_files.append(uploaded_file)
                    
                    # Set default message about file upload
                    st.session_state.user_input = f"I've uploaded {uploaded_file.name}. Can you help me analyze this file?"
                    
                    # Rerun to update UI
                    st.rerun()
        
        with cols[1]:
            # Text input field
            user_input = st.text_input(
                "Message",
                value=st.session_state.user_input,
                key="input_field",
                label_visibility="collapsed",
                placeholder="Type your message here..."
            )
        
        with cols[2]:
            # Send button
            send_btn = st.button(
                "Send",
                type="primary",
                key="send_btn"
            )
            
            # Style the send button as a circle with icon
            st.markdown(
                """
                <style>
                div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button {
                    border-radius: 50%;
                    width: 36px;
                    height: 36px;
                    padding: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background-color: #E53935;
                }
                div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button p {
                    display: none;
                }
                div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button::before {
                    content: "➤";
                    display: block;
                    width: 20px;
                    height: 20px;
                    text-align: center;
                    line-height: 20px;
                    color: white;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process input when send button is clicked
    if send_btn and user_input.strip():
        process_user_input(user_input.strip())

def process_user_input(user_input: str):
    """Process user input and generate agent response"""
    # Add user message to history
    st.session_state.history.append({
        "role": "user",
        "content": user_input
    })
    
    # Clear input field
    st.session_state.user_input = ""
    
    # Set typing indicator
    st.session_state.typing = True
    
    # Initialize agent if needed
    if "agent" not in st.session_state:
        st.session_state.agent = ReactAgent(max_steps=st.session_state.max_steps)
    
    # Run agent in a separate thread to allow typing indicator to show
    run_agent(user_input)

def run_agent(user_input: str):
    """Run the agent loop for a user query"""
    # Reset step counter for new query
    st.session_state.step_count = 0
    st.session_state.agent_steps = []
    
    # Reset agent
    st.session_state.agent.reset()
    
    # Run the agent loop
    while True:
        # Execute a single step
        step_result = st.session_state.agent.execute_step(user_input)
        
        # Update step count
        st.session_state.step_count = st.session_state.agent.current_step
        
        # Add to agent steps
        st.session_state.agent_steps.append(step_result)
        
        # If agent finishes or reaches max steps, break
        if step_result["action"] == "finish":
            # Add final response to chat history
            st.session_state.history.append({
                "role": "agent",
                "content": step_result["observation"]
            })
            break
        
        # For the first step, show the observation directly
        if len(st.session_state.agent_steps) == 1:
            st.session_state.history.append({
                "role": "agent",
                "content": step_result["observation"]
            })
            break
    
    # Clear typing indicator
    st.session_state.typing = False

def render_settings():
    """Render settings in sidebar"""
    with st.sidebar:
        st.markdown("<div style='text-align:center; margin-bottom:15px;'>⚙️ <b>Agent Settings</b></div>", unsafe_allow_html=True)
        
        # Max steps slider
        st.session_state.max_steps = st.slider(
            "Maximum Steps",
            min_value=3,
            max_value=15,
            value=st.session_state.max_steps,
            step=1,
            help="Maximum number of reasoning steps the agent can take for each query"
        )
        
        # Toggle for showing thought process
        st.session_state.show_thoughts = st.toggle(
            "Show Thought Process",
            value=st.session_state.show_thoughts,
            help="Display the agent's step-by-step reasoning"
        )
        
        # File management
        if st.session_state.uploaded_files:
            st.markdown("### Uploaded Files")
            for idx, file in enumerate(st.session_state.uploaded_files):
                # Show filename and size
                st.markdown(f"{idx+1}. **{file.name}** ({len(file.getvalue())} bytes)")
        
        # Reset conversation button
        if st.button("Reset Conversation", type="secondary"):
            # Clear conversation history
            st.session_state.history = []
            st.session_state.agent_steps = []
            st.session_state.step_count = 0
            st.session_state.uploaded_files = []
            st.session_state.typing = False
            
            # Reset intro flag
            st.session_state.intro_done = False
            
            # Force UI update
            st.rerun()

def send_intro_message():
    """Send an introductory message from the agent"""
    if not st.session_state.intro_done:
        st.session_state.history.append({
            "role": "agent",
            "content": """Hello! I'm your ReAct Agent assistant.

I can help you with:
- Answering questions
- Performing calculations
- Running Python code
- Analyzing uploaded files
- Breaking down complex problems

Just send me a message or upload a file to get started!"""
        })
        st.session_state.intro_done = True

# --------------------
# ---- MAIN APP ----
# --------------------
def main():
    """Main application entry point"""
    # Load custom CSS
    load_css()
    
    # Initialize session state
    init_session_state()
    
    # Send intro message if first time
    send_intro_message()
    
    # Render header
    render_header()
    
    # Render settings sidebar
    render_settings()
    
    # Main container for chat UI
    main_container = st.container()
    
    with main_container:
        # Render chat messages
        render_chat_messages()
        
        # Render input area
        render_input_area()
        
        # Render thought process
        render_thought_process()

if __name__ == "__main__":
    main()
