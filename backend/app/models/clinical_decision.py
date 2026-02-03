from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ClinicalQuery(BaseModel):
    """Schema for clinical decision query."""
    query: str = Field(..., min_length=10, description="Medical question or case description")
    document_ids: List[str] = Field(default=[], description="IDs of documents to reference")
    include_history: bool = Field(default=True, description="Include user's medical history")


class Citation(BaseModel):
    """Citation reference to source document."""
    document_id: str
    document_name: str
    excerpt: str
    relevance_score: float


class ClinicalDecisionBase(BaseModel):
    """Base clinical decision schema."""
    query: str
    decision: str  # AI-generated clinical decision
    confidence_score: Optional[float] = None
    citations: List[Citation] = []


class ClinicalDecisionCreate(ClinicalDecisionBase):
    """Schema for creating clinical decision."""
    user_id: str
    document_ids: List[str]
    metadata: Dict[str, Any] = {}


class ClinicalDecisionInDB(ClinicalDecisionBase):
    """Clinical decision schema as stored in database."""
    id: str = Field(alias="_id")
    user_id: str
    document_ids: List[str]
    created_at: datetime
    metadata: Dict[str, Any] = {}
    
    class Config:
        populate_by_name = True


class ClinicalDecision(ClinicalDecisionBase):
    """Clinical decision schema for API responses."""
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClinicalDecisionHistory(BaseModel):
    """Schema for clinical decision history listing."""
    id: str
    query: str
    decision_summary: str  # First 200 chars of decision
    created_at: datetime
    document_count: int
