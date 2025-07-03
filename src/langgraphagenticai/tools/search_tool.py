# src/langgraphagenticai/tools/search_tool.py

from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode

def get_tools():
    """
    Return the list of tools to be used in the chatbot
    """
    tavily_tool = TavilySearch(
        max_results=5,
        include_answer=True
    )
    return [tavily_tool]

def create_tool_node(tools):
    """
    Creates and returns a tool node for the graph
    """
    return ToolNode(tools=tools)
