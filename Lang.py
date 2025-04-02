import streamlit as st
from typing import Any, Dict, List, Optional, Union, Callable
import json
from datetime import datetime

# LangChain imports
from langchain.llms.base import LLM
from langchain.agents import AgentType, initialize_agent, Tool, AgentExecutor
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain.schema import AgentAction, AgentFinish, LLMResult
from langchain.tools import BaseTool
from langchain.chains import LLMMathChain
from langchain.memory import ConversationBufferMemory

# Create a custom LLM class that inherits from LangChain's LLM
class CustomLLM(LLM):
    """Custom LLM wrapper for abc_response function."""
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "custom"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call the custom LLM with the provided prompt."""
        try:
            # Use the abc_response function
            response = abc_response(prompt)
            
            # Handle stop sequences if provided
            if stop:
                for sequence in stop:
                    if sequence in response:
                        response = response.split(sequence)[0]
            
            return response
        except Exception as e:
            return f"Error: {str(e)}"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get identifying parameters."""
        return {"model": "custom_abc_response"}

# Create a custom callback handler to track agent steps for display
class StreamlitCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.steps = []
        
    def on_agent_action(self, action: AgentAction, **kwargs) -> Any:
        """Run on agent action."""
        self.steps.append({
            "type": "action",
            "tool": action.tool, 
            "tool_input": action.tool_input,
            "log": action.log
        })
    
    def on_tool_end(self, output: str, **kwargs) -> Any:
        """Run on tool end."""
        if self.steps:
            self.steps[-1]["output"] = output
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs) -> Any:
        """Run on agent end."""
        self.steps.append({
            "type": "finish",
            "output": finish.return_values["output"],
            "log": finish.log if hasattr(finish, "log") else ""
        })

# Custom date tool
def date_tool(query: str) -> str:
    """Get the current date and time or answer date-related questions."""
    current_date = datetime.now()
    
    if "current date" in query.lower() or "today" in query.lower():
        return f"The current date is {current_date.strftime('%Y-%m-%d')}"
    elif "current time" in query.lower() or "now" in query.lower():
        return f"The current time is {current_date.strftime('%H:%M:%S')}"
    elif "day of week" in query.lower():
        return f"Today is {current_date.strftime('%A')}"
    elif "month" in query.lower():
        return f"The current month is {current_date.strftime('%B')}"
    elif "year" in query.lower():
        return f"The current year is {current_date.strftime('%Y')}"
    else:
        return f"Date information: {current_date.strftime('%Y-%m-%d %H:%M:%S')}"

# Simulated search tool
def search_tool(query: str) -> str:
    """Simulated search tool that returns information about common topics."""
    query = query.lower()
    
    predefined_answers = {
        "weather": "The weather search shows partly cloudy with a high of 72°F for today.",
        "news": "Top headlines: New technological advances in AI announced today.",
        "stock": "Recent stock market update: Major indices showed mixed performance.",
        "movie": "Popular movies currently showing include action, comedy and drama genres.",
        "restaurant": "Top rated restaurants in the area include Italian, Japanese, and American cuisine options.",
        "population": "The world population is approximately 8 billion people as of 2023.",
        "distance": "The distance information would depend on specific locations.",
        "president": "The current president information depends on your country and the current date.",
    }
    
    for key, value in predefined_answers.items():
        if key in query:
            return value
    
    return "I searched but couldn't find specific information on that topic."

# Function to create LangChain tools
def create_tools(llm: LLM) -> List[Tool]:
    """Create a list of tools for the agent."""
    # LLMMathChain for calculations
    llm_math_chain = LLMMathChain.from_llm(llm=llm)
    
    tools = [
        Tool(
            name="Calculator",
            func=llm_math_chain.run,
            description="Useful for performing mathematical calculations. Input should be a mathematical expression."
        ),
        Tool(
            name="DateInfo",
            func=date_tool,
            description="Useful for getting the current date, time, or answering date-related questions."
        ),
        Tool(
            name="Search",
            func=search_tool,
            description="Useful for finding information about various topics like weather, news, stocks, etc."
        )
    ]
    
    return tools

# Main Streamlit App
def main():
    st.title("LangChain ReAct Agent")
    st.markdown("Ask me anything! I can calculate, search, and provide date information.")
    
    # Initialize session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "agent" not in st.session_state:
        # Initialize the LLM
        llm = CustomLLM()
        
        # Create tools
        tools = create_tools(llm)
        
        # Create conversation memory
        memory = ConversationBufferMemory(memory_key="chat_history")
        
        # Initialize the agent - this is the standard LangChain way
        st.session_state.agent = initialize_agent(
            tools, 
            llm, 
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # Standard ReAct agent
            verbose=True,
            memory=memory,
            handle_parsing_errors=True
        )
    
    # Display chat messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # User input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Add to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Create callback handler for tracking steps
        callback_handler = StreamlitCallbackHandler()
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Run the agent with callbacks
                    response = st.session_state.agent.run(
                        user_input,
                        callbacks=[callback_handler]
                    )
                    
                    # Display the response
                    st.write(response)
                    
                    # Display the agent steps
                    if callback_handler.steps:
                        with st.expander("See agent's reasoning"):
                            for i, step in enumerate(callback_handler.steps):
                                if step["type"] == "action":
                                    st.markdown(f"**Thought**: {step['log']}")
                                    st.markdown(f"**Action**: {step['tool']}")
                                    st.markdown(f"**Action Input**: {step['tool_input']}")
                                    if "output" in step:
                                        st.markdown(f"**Observation**: {step['output']}")
                                    st.markdown("---")
                                elif step["type"] == "finish":
                                    st.markdown(f"**Final Thought**: {step['log']}")
                except Exception as e:
                    error_msg = f"An error occurred: {str(e)}"
                    st.error(error_msg)
                    response = "I encountered an error while processing your request. Please try again."
                    st.write(response)
        
        # Add to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
