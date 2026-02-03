from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
from app.models.document import Document, DocumentDetail
from app.models.user import User
from app.services.document_service import DocumentService
from app.services.auth_service import AuthService
from app.db.mongodb import get_database

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=Document, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(AuthService.get_current_user),
    db = Depends(get_database)
):
    """
    Upload and process a medical document (PDF/DOCX/TXT).
    
    Args:
        file: Document file to upload
        current_user: Current authenticated user
        db: Database connection
        
    Returns:
        Created document object
        
    Raises:
        HTTPException: If file type invalid or upload fails
    """
    service = DocumentService(db)
    return await service.upload_and_process(file, current_user.id)


@router.get("/", response_model=List[Document])
async def list_documents(
    current_user: User = Depends(AuthService.get_current_user),
    db = Depends(get_database)
):
    """
    Get all documents for the current user.
    
    Args:
        current_user: Current authenticated user
        db: Database connection
        
    Returns:
        List of user documents
    """
    service = DocumentService(db)
    return await service.get_user_documents(current_user.id)


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: str,
    current_user: User = Depends(AuthService.get_current_user),
    db = Depends(get_database)
):
    """
    Get detailed information about a specific document.
    
    Args:
        document_id: Document ID
        current_user: Current authenticated user
        db: Database connection
        
    Returns:
        Detailed document information
        
    Raises:
        HTTPException: If document not found or unauthorized
    """
    service = DocumentService(db)
    return await service.get_document(document_id, current_user.id)


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(AuthService.get_current_user),
    db = Depends(get_database)
):
    """
    Delete a document and all associated data.
    
    Args:
        document_id: Document ID
        current_user: Current authenticated user
        db: Database connection
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If document not found or unauthorized
    """
    service = DocumentService(db)
    return await service.delete_document(document_id, current_user.id)
