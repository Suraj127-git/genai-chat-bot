from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.clinical_decision import ClinicalQuery, ClinicalDecision, ClinicalDecisionHistory
from app.models.user import User
from app.services.clinical_service import ClinicalService
from app.services.auth_service import AuthService
from app.db.mongodb import get_database

router = APIRouter(prefix="/clinical", tags=["clinical"])


@router.post("/analyze", response_model=ClinicalDecision, status_code=status.HTTP_201_CREATED)
async def generate_clinical_decision(
    query: ClinicalQuery,
    current_user: User = Depends(AuthService.get_current_user),
    db = Depends(get_database)
):
    """
    Generate AI-powered clinical decision based on medical query and documents.
    
    This endpoint:
    1. Retrieves relevant document chunks from ChromaDB
    2. Generates clinical analysis using GroqAI and LangChain
    3. Provides evidence-based recommendations with citations
    4. Stores the decision in history
    
    Args:
        query: Clinical query with medical question and optional document IDs
        current_user: Current authenticated user
        db: Database connection
        
    Returns:
        Clinical decision with AI analysis, confidence score, and citations
        
    Raises:
        HTTPException: If generation fails
    """
    service = ClinicalService(db)
    return await service.generate_decision(query, current_user.id)


@router.get("/history", response_model=List[ClinicalDecisionHistory])
async def get_clinical_history(
    limit: int = 50,
    skip: int = 0,
    current_user: User = Depends(AuthService.get_current_user),
    db = Depends(get_database)
):
    """
    Get clinical decision history for the current user.
    
    Args:
        limit: Maximum number of results (default 50)
        skip: Number of results to skip for pagination (default 0)
        current_user: Current authenticated user
        db: Database connection
        
    Returns:
        List of historical clinical decisions with summaries
    """
    service = ClinicalService(db)
    return await service.get_user_history(current_user.id, limit, skip)


@router.get("/{decision_id}", response_model=ClinicalDecision)
async def get_clinical_decision(
    decision_id: str,
    current_user: User = Depends(AuthService.get_current_user),
    db = Depends(get_database)
):
    """
    Get a specific clinical decision by ID.
    
    Args:
        decision_id: Clinical decision ID
        current_user: Current authenticated user
        db: Database connection
        
    Returns:
        Full clinical decision with all details
        
    Raises:
        HTTPException: If decision not found or unauthorized
    """
    service = ClinicalService(db)
    return await service.get_decision_by_id(decision_id, current_user.id)


@router.get("/{decision_id}/download/pdf")
async def download_decision_pdf(
    decision_id: str,
    current_user: User = Depends(AuthService.get_current_user),
    db = Depends(get_database)
):
    """
    Download clinical decision as PDF report.
    
    Note: Implementation pending
    
    Args:
        decision_id: Clinical decision ID
        current_user: Current authenticated user
        db: Database connection
        
    Returns:
        PDF file download
    """
    service = ClinicalService(db)
    return await service.download_as_pdf(decision_id, current_user.id)


@router.get("/{decision_id}/download/docx")
async def download_decision_docx(
    decision_id: str,
    current_user: User = Depends(AuthService.get_current_user),
    db = Depends(get_database)
):
    """
    Download clinical decision as DOCX document.
    
    Note: Implementation pending
    
    Args:
        decision_id: Clinical decision ID
        current_user: Current authenticated user
        db: Database connection
        
    Returns:
        DOCX file download
    """
    service = ClinicalService(db)
    return await service.download_as_docx(decision_id, current_user.id)
