import os
import hashlib
from typing import List, Dict, Optional, Any
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams, PointStruct, PayloadSchemaType
from langchain_community.embeddings import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from src.langgraphagenticai.common.logger import logger
import numpy as np

class QdrantManager:
    """
    Manages Qdrant vector database operations for storing and retrieving Q&A pairs
    """
    
    def __init__(self, collection_name: str = "qa_collection", embedding_model: str = "nomic-embed-text"):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY", None)
        )
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Initialize embeddings based on model type
        if "gpt" in embedding_model.lower() or "openai" in embedding_model.lower():
            self.embeddings = OpenAIEmbeddings(
                model=embedding_model,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            # Default to Ollama embeddings
            self.embeddings = OllamaEmbeddings(
                model=embedding_model,
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            )
        
        self.vector_size = self._get_vector_size()
        self._ensure_collection_exists()
    
    def _get_vector_size(self) -> int:
        """Get the vector size for the embedding model"""
        try:
            # Create a sample embedding to determine vector size
            sample_text = "sample text for dimension detection"
            sample_embedding = self.embeddings.embed_query(sample_text)
            return len(sample_embedding)
        except Exception as e:
            logger.warning(f"Could not determine vector size automatically: {e}")
            # Default vector sizes for common models
            model_sizes = {
                "nomic-embed-text": 768,
                "text-embedding-ada-002": 1536,
                "text-embedding-3-small": 1536,
                "text-embedding-3-large": 3072,
                "llama3.2:1b": 384,
                "llama3:8b": 4096
            }
            return model_sizes.get(self.embedding_model, 768)
    
    def _ensure_collection_exists(self):
        """Ensure the collection exists, create if it doesn't"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                
                # Create index for usecase field to enable filtering
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="usecase",
                    field_schema=PayloadSchemaType.KEYWORD
                )
                
                logger.info(f"Collection {self.collection_name} created successfully with usecase index")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                # Check if index exists, create if not
                try:
                    collection_info = self.client.get_collection(self.collection_name)
                    # If the collection exists but doesn't have the index, create it
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name="usecase",
                        field_schema=PayloadSchemaType.KEYWORD
                    )
                    logger.info("Created usecase index on existing collection")
                except Exception as index_error:
                    # Index might already exist, which is fine
                    logger.debug(f"Index creation result: {index_error}")
                    
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def _generate_id(self, text: str) -> str:
        """Generate a unique ID for the text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def store_qa_pair(self, question: str, answer: str, usecase: str, metadata: Optional[Dict] = None) -> bool:
        """
        Store a question-answer pair in the vector database
        
        Args:
            question: The user question
            answer: The generated answer
            usecase: The use case (e.g., "Basic Chatbot", "AI News")
            metadata: Additional metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create embedding for the question
            question_embedding = self.embeddings.embed_query(question)
            
            # Prepare metadata
            payload = {
                "question": question,
                "answer": answer,
                "usecase": usecase,
                "timestamp": np.datetime64('now').astype('datetime64[s]').item().isoformat(),
                **(metadata or {})
            }
            
            # Create point
            point_id = self._generate_id(f"{question}_{usecase}")
            point = PointStruct(
                id=point_id,
                vector=question_embedding,
                payload=payload
            )
            
            # Upload to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Stored Q&A pair with ID: {point_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing Q&A pair: {e}")
            return False
    
    def search_similar_questions(self, query: str, usecase: str, limit: int = 5, 
                               score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Search for similar questions in the vector database
        
        Args:
            query: The user query
            usecase: The current use case
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of similar Q&A pairs
        """
        try:
            # Create embedding for the query
            query_embedding = self.embeddings.embed_query(query)
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="usecase",
                            match=models.MatchValue(value=usecase)
                        )
                    ]
                ),
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "question": result.payload["question"],
                    "answer": result.payload["answer"],
                    "score": result.score,
                    "metadata": {k: v for k, v in result.payload.items() 
                               if k not in ["question", "answer"]}
                })
            
            logger.info(f"Found {len(results)} similar questions for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar questions: {e}")
            return []
    
    def search_similar_questions_no_filter(self, query: str, limit: int = 5, 
                                         score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Search for similar questions without usecase filtering (fallback method)
        
        Args:
            query: The user query
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of similar Q&A pairs
        """
        try:
            # Create embedding for the query
            query_embedding = self.embeddings.embed_query(query)
            
            # Search in Qdrant without filtering
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "question": result.payload["question"],
                    "answer": result.payload["answer"],
                    "score": result.score,
                    "metadata": {k: v for k, v in result.payload.items() 
                               if k not in ["question", "answer"]}
                })
            
            logger.info(f"Found {len(results)} similar questions (no filter) for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar questions without filter: {e}")
            return []
    
    def create_missing_indexes(self) -> bool:
        """Create missing indexes for better performance"""
        try:
            # Create index for usecase field
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="usecase",
                field_schema=PayloadSchemaType.KEYWORD
            )
            
            # Create index for timestamp field (optional)
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="timestamp",
                field_schema=PayloadSchemaType.DATETIME
            )
            
            logger.info("Created missing indexes successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "total_points": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance.value
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def clear_collection(self) -> bool:
        """Clear all data from the collection"""
        try:
            self.client.delete_collection(self.collection_name)
            self._ensure_collection_exists()
            logger.info(f"Collection {self.collection_name} cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False