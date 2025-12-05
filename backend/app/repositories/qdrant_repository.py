from typing import List, Dict, Any, Optional
from backend.app.database.qdrant_manager import QdrantManager

class QdrantRepository:
    def __init__(self, collection_name: str = "qa_collection", embedding_model: str = "nomic-embed-text"):
        self.manager = QdrantManager(collection_name=collection_name, embedding_model=embedding_model)

    def search(self, query: str, usecase: str, limit: int = 5, score_threshold: float = 0.8) -> List[Dict[str, Any]]:
        return self.manager.search_similar_questions(query=query, usecase=usecase, limit=limit, score_threshold=score_threshold)

    def store(self, question: str, answer: str, usecase: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        return self.manager.store_qa_pair(question=question, answer=answer, usecase=usecase, metadata=metadata or {})

    def stats(self) -> Dict[str, Any]:
        return self.manager.get_collection_stats()

    def clear(self) -> bool:
        return self.manager.clear_collection()

