from langgraph.graph import StateGraph
from src.langgraphagenticai.state.state import State
from langgraph.graph import START, END
from src.langgraphagenticai.nodes.enhanced_chatbot_node import EnhancedChatbotNode
from src.langgraphagenticai.nodes.enhanced_ai_news_node import EnhancedAINewsNode
from src.langgraphagenticai.tools.search_tool import get_tools, create_tool_node
from langgraph.prebuilt import tools_condition
from src.langgraphagenticai.nodes.chatbot_with_Tool_node import ChatbotWithToolNode
from src.langgraphagenticai.common.logger import logger
from src.langgraphagenticai.database.qdrant_manager import QdrantManager
import traceback

class EnhancedGraphBuilder:
    """
    Enhanced Graph Builder with Qdrant vector database integration
    """
    
    def __init__(self, model, embedding_model: str = "nomic-embed-text"):
        self.llm = model
        self.embedding_model = embedding_model
        self.graph_builder = StateGraph(State)
        self.qdrant_manager = QdrantManager(embedding_model=embedding_model)
    
    def enhanced_basic_chatbot_build_graph(self):
        """
        Builds an enhanced basic chatbot graph with vector database integration
        """
        logger.info("Building enhanced basic chatbot graph")
        
        enhanced_chatbot_node = EnhancedChatbotNode(
            model=self.llm,
            embedding_model=self.embedding_model
        )
        
        self.graph_builder.add_node("chatbot", enhanced_chatbot_node.process)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("chatbot", END)
    
    def enhanced_ai_news_builder_graph(self):
        """
        Builds an enhanced AI news graph with vector database integration
        """
        logger.info("Building enhanced AI news graph")
        
        enhanced_ai_news_node = EnhancedAINewsNode(
            model=self.llm,
            embedding_model=self.embedding_model
        )
        
        # Add nodes
        self.graph_builder.add_node("fetch_news", enhanced_ai_news_node.fetch_news)
        self.graph_builder.add_node("summarize_news", enhanced_ai_news_node.summarize_news)
        self.graph_builder.add_node("save_result", enhanced_ai_news_node.save_result)
        
        # Add edges
        self.graph_builder.set_entry_point("fetch_news")
        self.graph_builder.add_edge("fetch_news", "summarize_news")
        self.graph_builder.add_edge("summarize_news", "save_result")
        self.graph_builder.add_edge("save_result", END)
    
    def chatbot_with_tools_build_graph(self):
        """
        Builds chatbot with tools graph (unchanged for now)
        """
        logger.info("Building chatbot with tools graph")
        
        # Define the tool and tool node
        tools = get_tools()
        tool_node = create_tool_node(tools)
        
        # Define the chatbot node
        obj_chatbot_with_node = ChatbotWithToolNode(self.llm)
        chatbot_node = obj_chatbot_with_node.create_chatbot(tools)
        
        # Add nodes
        self.graph_builder.add_node("chatbot", chatbot_node)
        self.graph_builder.add_node("tools", tool_node)
        
        # Define conditional and direct edges
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_conditional_edges("chatbot", tools_condition)
        self.graph_builder.add_edge("tools", "chatbot")
    
    def setup_graph(self, usecase: str):
        """
        Sets up the enhanced graph for the selected use case
        """
        try:
            logger.info(f"Setting up enhanced graph for use case: {usecase}")
            
            if usecase == "Basic Chatbot":
                self.enhanced_basic_chatbot_build_graph()
            elif usecase == "Chatbot With Web":
                self.chatbot_with_tools_build_graph()
            elif usecase == "AI News":
                self.enhanced_ai_news_builder_graph()
            else:
                logger.error(f"Invalid use case selected: {usecase}")
                raise ValueError(f"Invalid use case: {usecase}")
            
            logger.info("Enhanced graph setup completed successfully")
            return self.graph_builder.compile()
            
        except Exception as e:
            tb = traceback.format_exc()
            logger.critical(f"Failed to setup enhanced graph for {usecase}: {e}\n{tb}")
            raise
    
    def get_database_stats(self):
        """
        Get statistics about the vector database
        """
        return self.qdrant_manager.get_collection_stats()
    
    def clear_database(self):
        """
        Clear the vector database
        """
        return self.qdrant_manager.clear_collection()
