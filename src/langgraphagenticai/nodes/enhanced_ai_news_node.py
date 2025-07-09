from src.langgraphagenticai.state.state import State
from src.langgraphagenticai.common.logger import logger
from src.langgraphagenticai.database.qdrant_manager import QdrantManager
from src.langgraphagenticai.nodes.ai_news_node import AINewsNode
from typing import Dict, Any
import json

class EnhancedAINewsNode(AINewsNode):
    """
    Enhanced AI News Node with vector database integration
    """
    
    def __init__(self, model, embedding_model: str = "nomic-embed-text"):
        super().__init__(model)
        self.qdrant_manager = QdrantManager(
            collection_name="ai_news_collection",
            embedding_model=embedding_model
        )
        self.similarity_threshold = 0.75
    
    def fetch_news(self, state: State) -> Dict[str, Any]:
        """
        Enhanced fetch_news that checks for similar news requests
        """
        logger.info("Enhanced AI News: Fetching news with vector search")
        
        # Get user message/timeframe
        messages = state.get('messages', [])
        if messages:
            user_query = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        else:
            user_query = state.get('user_message', 'latest AI news')
        
        # Search for similar news requests
        similar_requests = self.qdrant_manager.search_similar_questions(
            query=user_query,
            usecase="AI News",
            limit=3,
            score_threshold=self.similarity_threshold
        )
        
        # If we find a recent similar request, return cached news
        if similar_requests:
            logger.info(f"Found similar news request with score: {similar_requests[0]['score']}")
            # You might want to check timestamp to ensure news is recent
            cached_news = similar_requests[0]['answer']
            
            # Parse cached news if it's JSON
            try:
                if isinstance(cached_news, str) and cached_news.startswith('{'):
                    cached_data = json.loads(cached_news)
                    return {"news_data": cached_data, "from_cache": True}
            except json.JSONDecodeError:
                logger.warning("Could not parse cached news data")
        
        # Fetch new news using parent method
        result = super().fetch_news(state)
        
        # Store the news request and data
        news_data = result.get('news_data', {})
        self.qdrant_manager.store_qa_pair(
            question=user_query,
            answer=json.dumps(news_data) if news_data else "No news data available",
            usecase="AI News",
            metadata={"type": "news_fetch", "from_cache": False}
        )
        
        return result
    
    def summarize_news(self, state: State) -> Dict[str, Any]:
        """
        Enhanced summarize_news that can work with cached data
        """
        logger.info("Enhanced AI News: Summarizing news")
        
        # Check if data is from cache
        from_cache = state.get('from_cache', False)
        if from_cache:
            logger.info("Processing cached news data")
        
        # Use parent method for summarization
        result = super().summarize_news(state)
        
        # Store the summary
        summary = result.get('summary', '')
        if summary:
            news_data = state.get('news_data', {})
            query = f"AI news summary for {news_data.get('timeframe', 'recent')}"
            
            self.qdrant_manager.store_qa_pair(
                question=query,
                answer=summary,
                usecase="AI News",
                metadata={"type": "news_summary", "from_cache": from_cache}
            )
        
        return result
