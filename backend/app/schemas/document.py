"""
Document Schemas
Pydantic models for document CRUD operations
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DocumentCreate(BaseModel):
    """Schema for creating a document"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    document_type: str = Field(..., description="pdf, docx, txt, code, url, etc.")
    content: Optional[str] = Field(None, description="Full text content")
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    is_public: bool = Field(False)
    tags: Optional[List[str]] = Field(default_factory=list)
    doc_metadata: Optional[dict] = Field(default_factory=dict)


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    content: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None
    doc_metadata: Optional[dict] = None


class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: str
    title: str
    description: Optional[str]
    document_type: str
    organization_id: str
    file_name: Optional[str]
    file_size: Optional[int]
    mime_type: Optional[str]
    summary: Optional[str]
    is_indexed: bool
    is_active: bool
    is_public: bool
    processing_status: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    """Detailed document response with content"""
    content: Optional[str]
    vector_ids: List[str]
    embedding_model: str
    doc_metadata: dict
    processing_error: Optional[str]


class DocumentListResponse(BaseModel):
    """Response for listing documents"""
    id: str
    title: str
    description: Optional[str]
    document_type: str
    file_name: Optional[str]
    is_public: bool
    processing_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentSearchResponse(BaseModel):
    """Response for searching documents"""
    results: List[DocumentListResponse]
    query: str
    total: int
