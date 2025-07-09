from src.langgraphagenticai.state.state import State
from src.langgraphagenticai.common.logger import logger
from src.langgraphagenticai.database.qdrant_manager import QdrantManager
from typing import Dict, Any

class EnhancedChatbotNode:
    """
    Enhanced Chatbot with vector database integration for similar question retrieval
    """
    
    def __init__(self, model, embedding_model: str = "nomic-embed-text"):
        self.llm = model
        self.qdrant_manager = QdrantManager(embedding_model=embedding_model)
        self.similarity_threshold = 0.8  # Adjust based on your needs
    
    def process(self, state: State) -> Dict[str, Any]:
        """
        Enhanced process method that checks for similar questions before generating new responses
        """
        logger.info(f"EnhancedChatbotNode processing state: {state}")
        
        # Get the latest message
        messages = state.get('messages', [])
        if not messages:
            logger.warning("No messages found in state")
            return {"messages": []}
        
        # Extract user question (assuming last message is user input)
        user_question = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        usecase = state.get('usecase', 'Basic Chatbot')
        
        # Search for similar questions
        similar_questions = self.qdrant_manager.search_similar_questions(
            query=user_question,
            usecase=usecase,
            limit=3,
            score_threshold=self.similarity_threshold
        )
        
        # If we find a highly similar question, return the cached answer
        if similar_questions and similar_questions[0]['score'] > self.similarity_threshold:
            logger.info(f"Found similar question with score: {similar_questions[0]['score']}")
            cached_answer = similar_questions[0]['answer']
            
            # Optionally modify the cached answer to indicate it's from cache
            enhanced_answer = f"{cached_answer}\n\n*[This response was retrieved from previous similar questions]*"
            
            return {"messages": [enhanced_answer]}
        
        # Generate new response using LLM
        logger.info("No similar questions found, generating new response")
        response = self.llm.invoke(state['messages'])
        
        # Store the new Q&A pair
        if hasattr(response, 'content'):
            answer_content = response.content
        else:
            answer_content = str(response)
        
        self.qdrant_manager.store_qa_pair(
            question=user_question,
            answer=answer_content,
            usecase=usecase,
            metadata={"model": str(self.llm), "method": "llm_generated"}
        )
        
        return {"messages": response}
