"""
Document Model
Represents documents uploaded to the knowledge base
"""

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON, Index, BigInteger
from sqlalchemy.orm import relationship
from .base import BaseModel


class Document(BaseModel):
    """Document entity for knowledge base and RAG"""
    __tablename__ = "documents"
    __table_args__ = (
        Index('ix_documents_organization_id', 'organization_id'),
        Index('ix_documents_document_type', 'document_type'),
        Index('ix_documents_is_active', 'is_active'),
        {"comment": "Documents for knowledge base and RAG"}
    )
    
    # Basic info
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Organization reference
    organization_id = Column(
        String(36),
        ForeignKey('organizations.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Document metadata
    document_type = Column(
        String(50),
        nullable=False,
        comment="pdf, docx, txt, code, url, etc."
    )
    file_name = Column(String(500), nullable=True)
    file_path = Column(String(1000), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Content
    content = Column(Text, nullable=True, comment="Full text content")
    summary = Column(Text, nullable=True, comment="AI-generated summary")
    
    # Vector/RAG
    vector_ids = Column(
        JSON,
        default=list,
        nullable=False,
        comment="Vector IDs in Qdrant"
    )
    embedding_model = Column(
        String(100),
        default="text-embedding-3-small",
        comment="Model used for embeddings"
    )
    is_indexed = Column(Boolean, default=False, comment="Whether document is indexed in vector DB")
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_public = Column(Boolean, default=False)
    
    # Processing
    processing_status = Column(
        String(50),
        default="pending",
        comment="pending, processing, completed, failed"
    )
    processing_error = Column(Text, nullable=True)
    
    # Metadata
    tags = Column(
        JSON,
        default=list,
        nullable=False,
        comment="Tags for categorization"
    )
    doc_metadata = Column(
        JSON,
        default=dict,
        nullable=False,
        comment="Additional metadata (source, version, etc.)"
    )
    
    # Relationships
    organization = relationship(
        "Organization",
        back_populates="documents",
        foreign_keys=[organization_id]
    )
