from typing import List, Dict, Any, Optional
from langgraph.graph import MessagesState
from src.langgraphagenticai.state.state import State

class EnhancedState(State):
    """
    Enhanced state with vector database context
    """
    
    # Vector database related fields
    vector_search_results: Optional[List[Dict[str, Any]]] = None
    from_cache: bool = False
    cache_hit_score: float = 0.0
    
    # User preferences
    similarity_threshold: float = 0.8
    vector_search_limit: int = 5
    
    # Metadata
    usecase: str = "Basic Chatbot"
    embedding_model: str = "nomic-embed-text"
    
    # AI News specific
    news_sources: Optional[List[str]] = None
    summary_length: str = "Detailed"
    timeframe: str = "last 24 hours"
