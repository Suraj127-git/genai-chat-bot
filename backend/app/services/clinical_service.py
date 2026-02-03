from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from bson import ObjectId
from app.models.clinical_decision import (
    ClinicalQuery,
    ClinicalDecision,
    ClinicalDecisionCreate,
    ClinicalDecisionHistory,
    Citation
)
from app.chains.clinical_chain import ClinicalChain
from app.db.chromadb import ChromaDBManager
from app.services.document_service import DocumentService
import logging

logger = logging.getLogger(__name__)


class ClinicalService:
    """Service for clinical decision generation and management."""
    
    def __init__(self, db):
        self.db = db
        self.decisions_collection = db["clinical_decisions"]
        self.documents_collection = db["documents"]
        self.chroma_client = ChromaDBManager.get_client()
        self.clinical_chain = ClinicalChain()
    
    async def generate_decision(self, query: ClinicalQuery, user_id: str) -> ClinicalDecision:
        """
        Generate a clinical decision based on user query and documents.
        
        Args:
            query: Clinical query with question and document references
            user_id: User ID
            
        Returns:
            Clinical decision with AI-generated analysis
            
        Raises:
            HTTPException: If generation fails
        """
        try:
            # Retrieve relevant document chunks from ChromaDB
            context_documents = await self._get_relevant_context(
                user_id,
                query.query,
                query.document_ids
            )
            
            # Generate clinical decision using LangChain
            result = self.clinical_chain.generate_clinical_decision(
                query=query.query,
                context_documents=context_documents
            )
            
            # Create citations from result
            citations = [
                Citation(**cite) for cite in result.get("citations", [])
            ]
            
            # Save decision to database
            decision_dict = {
                "user_id": user_id,
                "query": query.query,
                "decision": result["decision"],
                "confidence_score": result.get("confidence_score"),
                "citations": [cite.dict() for cite in citations],
                "document_ids": query.document_ids,
                "created_at": datetime.utcnow(),
                "metadata": {
                    "model": result.get("model", "unknown"),
                    "context_documents_used": result.get("context_used", 0)
                }
            }
            
            db_result = await self.decisions_collection.insert_one(decision_dict)
            
            return ClinicalDecision(
                id=str(db_result.inserted_id),
                query=query.query,
                decision=result["decision"],
                confidence_score=result.get("confidence_score"),
                citations=citations,
                created_at=decision_dict["created_at"]
            )
            
        except Exception as e:
            logger.error(f"Error generating clinical decision: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate clinical decision: {str(e)}"
            )
    
    async def _get_relevant_context(
        self,
        user_id: str,
        query: str,
        document_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks for the query.
        
        Args:
            user_id: User ID
            query: Clinical query
            document_ids: Optional list of specific document IDs to search
            
        Returns:
            List of relevant document chunks with metadata
        """
        collection_name = f"user_{user_id}_documents"
        
        try:
            collection = self.chroma_client.get_or_create_collection(name=collection_name)
        except Exception as e:
            logger.warning(f"Could not access ChromaDB collection: {e}")
            return []
        
        # Build filter for specific documents if provided
        where_filter = None
        if document_ids:
            where_filter = {"document_id": {"$in": document_ids}}
        
        # Query ChromaDB for relevant chunks
        try:
            results = collection.query(
                query_texts=[query],
                n_results=10,  # Top 10 most relevant chunks
                where=where_filter
            )
            
            # Format results
            context_documents = []
            if results and results.get('documents') and len(results['documents']) > 0:
                for i, doc_text in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                    distance = results['distances'][0][i] if results.get('distances') else 1.0
                    
                    # Get document name from database
                    doc_id = metadata.get('document_id', '')
                    doc_name = await self._get_document_name(doc_id)
                    
                    context_documents.append({
                        "content": doc_text,
                        "metadata": {
                            **metadata,
                            "document_name": doc_name
                        },
                        "relevance_score": 1.0 - distance  # Convert distance to similarity
                    })
            
            return context_documents
            
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return []
    
    async def _get_document_name(self, document_id: str) -> str:
        """Get document filename from database."""
        if not document_id:
            return "Unknown Document"
        
        try:
            doc = await self.documents_collection.find_one({"_id": ObjectId(document_id)})
            return doc.get("filename", "Unknown Document") if doc else "Unknown Document"
        except:
            return "Unknown Document"
    
    async def get_user_history(
        self,
        user_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> List[ClinicalDecisionHistory]:
        """
        Get clinical decision history for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            skip: Number of results to skip (pagination)
            
        Returns:
            List of historical clinical decisions
        """
        cursor = self.decisions_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        history = []
        async for decision in cursor:
            # Create summary (first 200 chars of decision)
            decision_text = decision.get("decision", "")
            summary = decision_text[:200] + "..." if len(decision_text) > 200 else decision_text
            
            history.append(ClinicalDecisionHistory(
                id=str(decision["_id"]),
                query=decision["query"],
                decision_summary=summary,
                created_at=decision["created_at"],
                document_count=len(decision.get("document_ids", []))
            ))
        
        return history
    
    async def get_decision_by_id(self, decision_id: str, user_id: str) -> ClinicalDecision:
        """
        Get a specific clinical decision.
        
        Args:
            decision_id: Decision ID
            user_id: User ID (for authorization)
            
        Returns:
            Clinical decision object
            
        Raises:
            HTTPException: If not found or unauthorized
        """
        decision = await self.decisions_collection.find_one({"_id": ObjectId(decision_id)})
        
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clinical decision not found"
            )
        
        if decision["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this decision"
            )
        
        citations = [Citation(**cite) for cite in decision.get("citations", [])]
        
        return ClinicalDecision(
            id=str(decision["_id"]),
            query=decision["query"],
            decision=decision["decision"],
            confidence_score=decision.get("confidence_score"),
            citations=citations,
            created_at=decision["created_at"]
        )
    
    async def download_as_pdf(self, decision_id: str, user_id: str):
        """
        Generate and download clinical decision as PDF.
        
        TODO: Implement PDF generation using ReportLab
        """
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF download not yet implemented"
        )
    
    async def download_as_docx(self, decision_id: str, user_id: str):
        """
        Generate and download clinical decision as DOCX.
        
        TODO: Implement DOCX generation using python-docx
        """
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="DOCX download not yet implemented"
        )
