import os
import pandas as pd
from typing import Annotated, Sequence, TypedDict

from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage
from langchain_experimental.tools.python.tool import PythonAstREPLTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Define the state of our agent
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]

def create_graph(df: pd.DataFrame):
    """
    Creates a LangGraph agent capable of analyzing the provided DataFrame.
    """
    
    llm = ChatGroq(
        temperature=0,
        model_name="llama-3.3-70b-versatile", # Updated model
        api_key=os.environ.get("GROQ_API_KEY")
    )

    python_tool = PythonAstREPLTool(locals={"df": df})
    python_tool.name = "python_interpreter"
    python_tool.description = (
        "A Python shell. Use this to execute python commands. "
        "Input should be a valid python command. "
        "The dataframe is available as 'df'. "
        "ALWAYS print the final result using `print(...)` so I can see it."
    )

    tools = [python_tool]
    llm_with_tools = llm.bind_tools(tools)

    def chatbot(state: AgentState):
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    workflow = StateGraph(AgentState)

    workflow.add_node("chatbot", chatbot)
    workflow.add_node("tools", tool_node)

    workflow.set_entry_point("chatbot")

    def should_continue(state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    workflow.add_conditional_edges(
        "chatbot",
        should_continue,
    )
    workflow.add_edge("tools", "chatbot")

    app = workflow.compile()
    return app
