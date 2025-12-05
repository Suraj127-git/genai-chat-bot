import os
import hashlib
from typing import List, Dict, Optional, Any
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams, PointStruct, PayloadSchemaType
from langchain_community.embeddings import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from backend.app.common.logger import logger
import numpy as np

class QdrantManager:
    def __init__(self, collection_name: str = "qa_collection", embedding_model: str = "nomic-embed-text"):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY", None)
        )
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        if "gpt" in embedding_model.lower() or "openai" in embedding_model.lower():
            self.embeddings = OpenAIEmbeddings(
                model=embedding_model,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            self.embeddings = OllamaEmbeddings(
                model=embedding_model,
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            )
        self.vector_size = self._get_vector_size()
        self._ensure_collection_exists()

    def _get_vector_size(self) -> int:
        try:
            sample_embedding = self.embeddings.embed_query("sample text for dimension detection")
            return len(sample_embedding)
        except Exception as e:
            logger.warning(f"Could not determine vector size automatically: {e}")
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
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
                )
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="usecase",
                    field_schema=PayloadSchemaType.KEYWORD
                )
            else:
                try:
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name="usecase",
                        field_schema=PayloadSchemaType.KEYWORD
                    )
                except Exception as index_error:
                    logger.debug(f"Index creation result: {index_error}")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise

    def _generate_id(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

    def store_qa_pair(self, question: str, answer: str, usecase: str, metadata: Optional[Dict] = None) -> bool:
        try:
            question_embedding = self.embeddings.embed_query(question)
            payload = {
                "question": question,
                "answer": answer,
                "usecase": usecase,
                "timestamp": np.datetime64('now').astype('datetime64[s]').item().isoformat(),
                **(metadata or {})
            }
            point_id = self._generate_id(f"{question}_{usecase}")
            point = PointStruct(id=point_id, vector=question_embedding, payload=payload)
            self.client.upsert(collection_name=self.collection_name, points=[point])
            logger.info(f"Stored Q&A pair with ID: {point_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing Q&A pair: {e}")
            return False

    def search_similar_questions(self, query: str, usecase: str, limit: int = 5, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        try:
            query_embedding = self.embeddings.embed_query(query)
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=models.Filter(must=[models.FieldCondition(key="usecase", match=models.MatchValue(value=usecase))]),
                limit=limit,
                score_threshold=score_threshold
            )
            results = []
            for result in search_results:
                results.append({
                    "question": result.payload["question"],
                    "answer": result.payload["answer"],
                    "score": result.score,
                    "metadata": {k: v for k, v in result.payload.items() if k not in ["question", "answer"]}
                })
            logger.info(f"Found {len(results)} similar questions for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Error searching similar questions: {e}")
            return []

