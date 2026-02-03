from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Types of documents that can be uploaded."""
    PDF = "pdf"
    TEXT = "txt"
    DOCX = "docx"
    DOC = "doc"


class DocumentBase(BaseModel):
    """Base document schema."""
    filename: str
    file_type: DocumentType
    file_size: int  # in bytes
    description: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Schema for document creation."""
    pass


class DocumentInDB(DocumentBase):
    """Document schema as stored in database."""
    id: str = Field(alias="_id")
    user_id: str
    file_path: str  # GridFS file ID or path
    extracted_text: Optional[str] = None
    chunk_ids: List[str] = []  # ChromaDB chunk IDs
    upload_date: datetime
    processed: bool = False
    processing_error: Optional[str] = None
    
    class Config:
        populate_by_name = True


class Document(DocumentBase):
    """Document schema for API responses."""
    id: str
    upload_date: datetime
    processed: bool
    
    class Config:
        from_attributes = True


class DocumentDetail(Document):
    """Detailed document schema with extracted text."""
    extracted_text: Optional[str] = None
    chunk_count: int = 0
