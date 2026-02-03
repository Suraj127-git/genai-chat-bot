from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from app.core.config import settings
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ClinicalChain:
    """LangChain for clinical decision generation."""
    
    def __init__(self):
        """Initialize the clinical decision chain."""
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model="mixtral-8x7b-32768",
            temperature=0.3,  # Lower temperature for more consistent medical advice
            max_tokens=4096
        )
        
        self.system_prompt = """You are an AI medical assistant designed to help healthcare professionals analyze patient cases and medical documents.

Your role is to:
1. Analyze the provided medical information and documents
2. Generate evidence-based clinical insights
3. Provide differential diagnoses when appropriate
4. Cite specific sections from the provided documents
5. Indicate confidence levels in your assessments

IMPORTANT GUIDELINES:
- Always cite your sources from the provided documents
- Acknowledge when information is insufficient
- Recommend further tests or consultations when appropriate
- Use clear, professional medical terminology
- Structure your response with clear sections (Assessment, Differential Diagnosis, Recommendations, etc.)
- Include confidence scores (High/Medium/Low) for key findings

DISCLAIMER: You are an AI assistant meant to support clinical decision-making, not replace professional medical judgment. All recommendations should be verified by qualified healthcare professionals."""

    def generate_clinical_decision(
        self,
        query: str,
        context_documents: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate clinical decision based on query and context.
        
        Args:
            query: Medical question or case description
            context_documents: List of relevant document chunks with metadata
            conversation_history: Optional conversation history
            
        Returns:
            Dict with decision, confidence, and citations
        """
        # Build context from documents
        context_text = self._build_context(context_documents)
        
        # Build messages
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Add conversation history if available
        if conversation_history:
            for msg in conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        
        # Add current query with context
        user_message = f"""Based on the following medical documents and information, please analyze this case:

MEDICAL DOCUMENTS:
{context_text}

CLINICAL QUESTION:
{query}

Please provide a comprehensive clinical assessment with citations to specific documents."""
        
        messages.append(HumanMessage(content=user_message))
        
        try:
            # Generate response
            response = self.llm.invoke(messages)
            decision_text = response.content
            
            # Extract confidence (simple heuristic - can be improved)
            confidence = self._estimate_confidence(decision_text, context_documents)
            
            # Extract citations
            citations = self._extract_citations(decision_text, context_documents)
            
            return {
                "decision": decision_text,
                "confidence_score": confidence,
                "citations": citations,
                "model": "mixtral-8x7b-32768",
                "context_used": len(context_documents)
            }
            
        except Exception as e:
            logger.error(f"Error generating clinical decision: {e}")
            raise
    
    def _build_context(self, context_documents: List[Dict[str, Any]]) -> str:
        """Build formatted context from document chunks."""
        if not context_documents:
            return "No medical documents provided."
        
        context_parts = []
        for i, doc in enumerate(context_documents, 1):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            doc_name = metadata.get("document_name", f"Document {i}")
            
            context_parts.append(f"""
[Document {i}: {doc_name}]
{content}
---
""")
        
        return "\n".join(context_parts)
    
    def _estimate_confidence(self, decision_text: str, context_documents: List[Dict[str, Any]]) -> float:
        """
        Estimate confidence score based on response characteristics.
        
        This is a simple heuristic. Can be improved with:
        - Analyzing certainty keywords
        - Checking document relevance scores
        - Using a separate confidence classifier
        """
        confidence = 0.5  # Base confidence
        
        # Increase confidence if multiple documents were used
        if len(context_documents) >= 3:
            confidence += 0.2
        
        # Increase confidence if response includes citations
        if any(marker in decision_text.lower() for marker in ["document", "according to", "as stated in", "per the"]):
            confidence += 0.15
        
        # Decrease confidence if uncertainty markers present
        uncertainty_markers = ["possibly", "might", "unclear", "insufficient information", "cannot determine"]
        uncertainty_count = sum(1 for marker in uncertainty_markers if marker in decision_text.lower())
        confidence -= min(uncertainty_count * 0.1, 0.3)
        
        # Clamp between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def _extract_citations(self, decision_text: str, context_documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract citations from the decision text.
        
        This is a simple implementation. Can be improved with:
        - NER for document references
        - Similarity matching between response sections and source documents
        """
        citations = []
        
        for doc in context_documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            # Simple check: if document content appears in decision (very basic)
            # In production, use more sophisticated citation extraction
            excerpt = content[:200] + "..." if len(content) > 200 else content
            
            citations.append({
                "document_id": metadata.get("document_id", ""),
                "document_name": metadata.get("document_name", "Unknown"),
                "excerpt": excerpt,
                "relevance_score": doc.get("relevance_score", 0.0)
            })
        
        return citations[:5]  # Return top 5 citations
