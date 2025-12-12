"""
Document Management CRUD Endpoints
Provides complete CRUD operations for documents and knowledge base
Integrates with Qdrant for vector indexing and semantic search
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models import Document, User
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentDetailResponse, DocumentListResponse
)
from app.schemas.common import ListResponse
from app.utils.security import get_current_user
from app.services.qdrant_service import qdrant_service
from app.services.embedding_service import embedding_service
import uuid
from datetime import datetime
import mimetypes
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/search/semantic", response_model=ListResponse[DocumentListResponse])
async def semantic_search_documents(
    query: str = Query(..., description="Semantic search query"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    min_score: float = Query(0.7, ge=0, le=1)
):
    """
    Perform semantic search across documents in user's organization
    
    Uses vector similarity to find relevant documents
    Returns ranked results by relevance score
    """
    try:
        # Generate query embedding
        query_embedding = await embedding_service.embed_text(query)
        if not query_embedding:
            raise HTTPException(status_code=400, detail="Failed to generate query embedding")
        
        # Search in Qdrant
        results = qdrant_service.search_similar(
            collection_name="documents",
            query_vector=query_embedding,
            organization_id=str(current_user.organization_id),
            limit=limit,
            score_threshold=min_score
        )
        
        # Get document details from database
        document_ids = [r["document_id"] for r in results]
        documents = db.query(Document).filter(Document.id.in_(document_ids)).all()
        
        # Create mapping for quick lookup
        doc_map = {d.id: d for d in documents}
        
        # Return documents in order of relevance scores
        ranked_documents = []
        for result in results:
            doc = doc_map.get(result["document_id"])
            if doc and doc.is_active:
                ranked_documents.append(doc)
        
        return ListResponse(
            data=ranked_documents,
            total=len(ranked_documents),
            skip=0,
            limit=limit,
            metadata={"search_type": "semantic", "query": query, "min_score": min_score}
        )
    except Exception as e:
        logger.error(f"Semantic search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")


@router.post("/search/hybrid", response_model=ListResponse[DocumentListResponse])
async def hybrid_search_documents(
    query: str = Query(..., description="Search query"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    min_score: float = Query(0.7, ge=0, le=1),
    semantic_weight: float = Query(0.7, ge=0, le=1),
    keyword_weight: float = Query(0.3, ge=0, le=1)
):
    """
    Perform hybrid search combining semantic and keyword matching
    
    Weights for combining results:
    - semantic_weight: importance of vector similarity (default 0.7)
    - keyword_weight: importance of keyword matching (default 0.3)
    
    Returns documents ranked by combined score
    """
    try:
        # Get user's documents
        user_documents = db.query(Document).filter(
            Document.organization_id == current_user.organization_id,
            Document.is_active == True
        ).all()
        
        if not user_documents:
            return ListResponse(data=[], total=0, skip=0, limit=limit, metadata={"search_type": "hybrid"})
        
        # Semantic search results
        query_embedding = await embedding_service.embed_text(query)
        semantic_results = {}
        if query_embedding:
            results = qdrant_service.search_similar(
                collection_name="documents",
                query_vector=query_embedding,
                organization_id=str(current_user.organization_id),
                limit=limit * 2,  # Get more for combining
                score_threshold=0  # No threshold for hybrid
            )
            semantic_results = {r["document_id"]: r.get("score", 0) for r in results}
        
        # Keyword search results
        query_lower = query.lower()
        keyword_results = {}
        for doc in user_documents:
            title_match = query_lower in doc.title.lower() if doc.title else False
            content_match = query_lower in doc.content.lower() if doc.content else False
            summary_match = query_lower in doc.summary.lower() if doc.summary else False
            
            if title_match or content_match or summary_match:
                # Calculate keyword score (higher for title match)
                score = 0
                if title_match:
                    score += 0.5
                if summary_match:
                    score += 0.3
                if content_match:
                    score += 0.2
                keyword_results[doc.id] = score
        
        # Combine results
        all_doc_ids = set(semantic_results.keys()) | set(keyword_results.keys())
        combined_scores = {}
        for doc_id in all_doc_ids:
            semantic_score = semantic_results.get(doc_id, 0) * semantic_weight
            keyword_score = keyword_results.get(doc_id, 0) * keyword_weight
            combined_scores[doc_id] = semantic_score + keyword_score
        
        # Filter by min_score and sort
        filtered_results = {
            doc_id: score 
            for doc_id, score in combined_scores.items() 
            if score >= min_score
        }
        sorted_doc_ids = sorted(filtered_results.items(), key=lambda x: x[1], reverse=True)
        
        # Get document objects in ranked order
        doc_map = {d.id: d for d in user_documents}
        ranked_documents = [doc_map[doc_id] for doc_id, _ in sorted_doc_ids if doc_id in doc_map][:limit]
        
        return ListResponse(
            data=ranked_documents,
            total=len(ranked_documents),
            skip=0,
            limit=limit,
            metadata={
                "search_type": "hybrid",
                "query": query,
                "semantic_weight": semantic_weight,
                "keyword_weight": keyword_weight
            }
        )
    except Exception as e:
        logger.error(f"Hybrid search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Hybrid search failed: {str(e)}")


@router.get("/", response_model=ListResponse[DocumentListResponse])
async def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    document_type: Optional[str] = None,
    processing_status: Optional[str] = None,
    include_inactive: bool = Query(False),
    public_only: bool = Query(False)
):
    """
    List documents in user's organization
    
    Users see documents in their organization
    Superusers see all documents
    """
    query = db.query(Document)
    
    # Filter by organization if not superuser
    if not current_user.is_superuser:
        query = query.filter(Document.organization_id == current_user.organization_id)
    
    # Filter active documents by default
    if not include_inactive:
        query = query.filter(Document.is_active == True)
    
    # Filter by public documents only
    if public_only:
        query = query.filter(Document.is_public == True)
    
    # Search by title or description
    if search:
        query = query.filter(
            (Document.title.ilike(f"%{search}%")) |
            (Document.description.ilike(f"%{search}%")) |
            (Document.tags.contains([search]))
        )
    
    # Filter by document type
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    # Filter by processing status
    if processing_status:
        query = query.filter(Document.processing_status == processing_status)
    
    total = query.count()
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    
    return ListResponse(
        data=documents,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get document details
    
    Users can access documents in their organization
    Public documents can be accessed by anyone
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check access permissions
    if not current_user.is_superuser:
        if document.organization_id != current_user.organization_id and not document.is_public:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return document


@router.post("/", response_model=DocumentDetailResponse)
async def create_document(
    document_data: DocumentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new document
    
    Users can create documents in their organization
    Document content is automatically indexed in Qdrant for semantic search
    """
    # Check if user has admin role or is superuser
    is_admin = current_user.is_superuser or (current_user.role and current_user.role.name.lower() == 'admin')
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can create documents")
    
    # Create document
    document = Document(
        id=str(uuid.uuid4()),
        title=document_data.title,
        description=document_data.description,
        document_type=document_data.document_type,
        content=document_data.content,
        file_name=document_data.file_name,
        file_size=document_data.file_size,
        mime_type=document_data.mime_type,
        is_public=document_data.is_public,
        organization_id=current_user.organization_id,
        tags=document_data.tags or [],
        doc_metadata=document_data.doc_metadata or {},
        processing_status="pending",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Index document in Qdrant asynchronously
    background_tasks.add_task(
        index_document_vector,
        document_id=document.id,
        title=document.title,
        content=document.content,
        organization_id=str(current_user.organization_id),
        description=document.description
    )
    
    return document


@router.put("/{document_id}", response_model=DocumentDetailResponse)
async def update_document(
    document_id: str,
    document_data: DocumentUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a document
    
    Only admins or document creator's organization can update
    Document vector is automatically re-indexed if content changes
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    is_admin = current_user.is_superuser or (current_user.role and current_user.role.name.lower() == 'admin')
    if not (is_admin and document.organization_id == current_user.organization_id):
        if document.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Track if content changed for re-indexing
    content_changed = document_data.content is not None and document_data.content != document.content
    
    # Update fields
    if document_data.title is not None:
        document.title = document_data.title
    if document_data.description is not None:
        document.description = document_data.description
    if document_data.content is not None:
        document.content = document_data.content
    if document_data.is_public is not None:
        document.is_public = document_data.is_public
    if document_data.tags is not None:
        document.tags = document_data.tags
    if document_data.doc_metadata is not None:
        document.doc_metadata = document_data.doc_metadata
    
    document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(document)
    
    # Re-index if content changed
    if content_changed:
        background_tasks.add_task(
            index_document_vector,
            document_id=document.id,
            title=document.title,
            content=document.content,
            organization_id=str(document.organization_id),
            description=document.description
        )
    
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a document (soft delete)
    
    Only admins can delete documents
    Document is removed from Qdrant vector index
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check admin permission
    is_admin = current_user.is_superuser or (current_user.role and current_user.role.name.lower() == 'admin')
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can delete documents")
    
    if document.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Soft delete
    document.is_active = False
    document.updated_at = datetime.utcnow()
    db.commit()
    
    # Remove from Qdrant asynchronously
    background_tasks.add_task(
        delete_document_vector,
        document_id=document_id,
        organization_id=str(document.organization_id)
    )
    
    return {"success": True, "message": "Document deleted"}


@router.post("/{document_id}/restore")
async def restore_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Restore a deleted document
    
    Only admins can restore documents
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check admin permission
    is_admin = current_user.is_superuser or (current_user.role and current_user.role.name.lower() == 'admin')
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can restore documents")
    
    if document.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Restore
    document.is_active = True
    document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(document)
    
    return document


@router.post("/{document_id}/index")
async def index_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Index a document in vector database
    
    This endpoint would integrate with Qdrant for embeddings
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    if document.organization_id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if content exists
    if not document.content:
        raise HTTPException(status_code=400, detail="Document has no content to index")
    
    # Update processing status
    document.processing_status = "processing"
    db.commit()
    
    # TODO: Integrate with Qdrant vector database
    # For now, just mark as indexed
    document.is_indexed = True
    document.processing_status = "completed"
    document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(document)
    
    return {"success": True, "message": "Document indexed", "document": document}


@router.get("/search/query")
async def search_documents(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Search documents by content
    
    Returns documents matching the search query
    """
    # Build search query
    search_query = db.query(Document)
    
    # Filter by organization
    if not current_user.is_superuser:
        search_query = search_query.filter(Document.organization_id == current_user.organization_id)
    
    # Search in title, description, content, and tags
    search_query = search_query.filter(
        (Document.title.ilike(f"%{query}%")) |
        (Document.description.ilike(f"%{query}%")) |
        (Document.content.ilike(f"%{query}%")) |
        (Document.tags.contains([query]))
    )
    
    # Filter active documents
    search_query = search_query.filter(Document.is_active == True)
    
    total = search_query.count()
    results = search_query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "results": results,
        "query": query,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }


@router.post("/{document_id}/tags")
async def add_document_tags(
    document_id: str,
    tags: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add tags to a document
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    is_admin = current_user.is_superuser or (current_user.role and current_user.role.name.lower() == 'admin')
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can modify document tags")
    
    # Add unique tags
    existing_tags = set(document.tags)
    for tag in tags:
        if tag not in existing_tags:
            document.tags.append(tag)
    
    document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(document)
    
    return document


@router.delete("/{document_id}/tags/{tag}")
async def remove_document_tag(
    document_id: str,
    tag: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a tag from a document
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    is_admin = current_user.is_superuser or (current_user.role and current_user.role.name.lower() == 'admin')
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can modify document tags")
    
    # Remove tag
    if tag in document.tags:
        document.tags.remove(tag)
    
    document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(document)
    
    return document


@router.get("/by-type/{document_type}")
async def get_documents_by_type(
    document_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get documents by type (pdf, docx, txt, code, url, etc.)
    """
    query = db.query(Document).filter(Document.document_type == document_type)
    
    # Filter by organization if not superuser
    if not current_user.is_superuser:
        query = query.filter(Document.organization_id == current_user.organization_id)
    
    # Filter active documents
    query = query.filter(Document.is_active == True)
    
    total = query.count()
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    
    return ListResponse(
        data=documents,
        total=total,
        skip=skip,
        limit=limit
    )


# ==================== VECTOR INDEXING HELPER FUNCTIONS ====================

async def index_document_vector(
    document_id: str,
    title: str,
    content: str,
    organization_id: str,
    description: Optional[str] = None
):
    """
    Index a document in Qdrant for semantic search
    Runs asynchronously as a background task
    """
    try:
        # Generate embedding for the document
        embedding = await embedding_service.embed_document(
            title=title,
            content=content,
            metadata=description or ""
        )
        
        if not embedding:
            logger.warning(f"Failed to generate embedding for document {document_id}")
            return
        
        # Add to Qdrant
        success = qdrant_service.add_document_vector(
            collection_name="documents",
            document_id=document_id,
            vector=embedding,
            metadata={
                "title": title,
                "type": "document",
                "description": description
            },
            organization_id=organization_id
        )
        
        if success:
            logger.info(f"Successfully indexed document {document_id} in Qdrant")
        else:
            logger.error(f"Failed to index document {document_id} in Qdrant")
    except Exception as e:
        logger.error(f"Error indexing document {document_id}: {str(e)}")


async def delete_document_vector(document_id: str, organization_id: str):
    """
    Remove document from Qdrant when it's deleted
    """
    try:
        success = qdrant_service.delete_document_vector(
            collection_name="documents",
            document_id=document_id,
            organization_id=organization_id
        )
        
        if success:
            logger.info(f"Successfully removed document {document_id} from Qdrant")
        else:
            logger.warning(f"Could not remove document {document_id} from Qdrant")
    except Exception as e:
        logger.error(f"Error removing document {document_id} from Qdrant: {str(e)}")

