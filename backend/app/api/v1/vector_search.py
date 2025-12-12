"""
Vector Search API Endpoints
Provides semantic search and vector similarity operations
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.services.qdrant_service import qdrant_service
from app.services.embedding_service import embedding_service

router = APIRouter(prefix="/api/v1/search", tags=["vector-search"])


# Request/Response Models
class VectorSearchRequest(BaseModel):
    """Request for vector similarity search"""
    query: str
    limit: Optional[int] = 10
    score_threshold: Optional[float] = 0.7


class SearchResult(BaseModel):
    """Single search result"""
    document_id: str
    score: float
    title: Optional[str] = None
    metadata: dict


class VectorSearchResponse(BaseModel):
    """Response from vector search"""
    success: bool
    query: str
    results: List[SearchResult]
    total_results: int


class SemanticSearchRequest(BaseModel):
    """Request for semantic search across collections"""
    query: str
    collection: Optional[str] = "documents"
    limit: Optional[int] = 10
    min_score: Optional[float] = 0.7


class CollectionInfoResponse(BaseModel):
    """Information about a collection"""
    name: str
    points_count: Optional[int] = 0
    vectors_count: Optional[int] = 0
    disk_data_size: Optional[int] = 0
    disk_index_size: Optional[int] = 0


class VectorHealthResponse(BaseModel):
    """Vector database health status"""
    status: str
    collections: int
    models: List[str]


@router.post("/vector-search", response_model=VectorSearchResponse)
async def vector_search(
    request: VectorSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Perform semantic vector search across documents
    
    Args:
        request: Vector search parameters
        current_user: Current authenticated user
        
    Returns:
        Search results with similarity scores
    """
    try:
        # Generate embedding for query
        query_embedding = await embedding_service.embed_text(request.query)
        if not query_embedding:
            raise HTTPException(status_code=400, detail="Failed to generate query embedding")
        
        # Search in documents collection
        results = qdrant_service.search_similar(
            collection_name="documents",
            query_vector=query_embedding,
            organization_id=str(current_user.organization_id),
            limit=request.limit,
            score_threshold=request.score_threshold
        )
        
        # Format results
        formatted_results = [
            SearchResult(
                document_id=r["document_id"],
                score=r["score"],
                title=r["metadata"].get("title"),
                metadata=r["metadata"]
            )
            for r in results
        ]
        
        return VectorSearchResponse(
            success=True,
            query=request.query,
            results=formatted_results,
            total_results=len(formatted_results)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/semantic-search")
async def semantic_search(
    request: SemanticSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Perform semantic search with custom collection
    
    Args:
        request: Semantic search parameters
        current_user: Current authenticated user
        
    Returns:
        Semantic search results
    """
    try:
        # Generate embedding
        query_embedding = await embedding_service.embed_text(request.query)
        if not query_embedding:
            raise HTTPException(status_code=400, detail="Failed to generate query embedding")
        
        # Search in specified collection
        results = qdrant_service.search_similar(
            collection_name=request.collection,
            query_vector=query_embedding,
            organization_id=str(current_user.organization_id),
            limit=request.limit,
            score_threshold=request.min_score
        )
        
        return {
            "success": True,
            "query": request.query,
            "collection": request.collection,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")


@router.get("/collection/{collection_name}", response_model=CollectionInfoResponse)
async def get_collection_info(
    collection_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get information about a collection
    
    Args:
        collection_name: Name of the collection
        current_user: Current authenticated user
        
    Returns:
        Collection statistics and information
    """
    try:
        info = qdrant_service.get_collection_info(collection_name)
        if not info:
            raise HTTPException(status_code=404, detail="Collection not found")
        
        return CollectionInfoResponse(**info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collection info: {str(e)}")


@router.get("/collections", response_model=dict)
async def list_collections(current_user: User = Depends(get_current_user)):
    """
    List all available collections
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of collection names
    """
    try:
        collections = qdrant_service.list_collections()
        return {
            "collections": collections,
            "total": len(collections)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list collections: {str(e)}")


@router.post("/create-collection")
async def create_collection(
    collection_name: str = Query(..., description="Name of the collection to create"),
    vector_size: Optional[int] = Query(1536, description="Vector dimension size"),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new vector collection
    
    Args:
        collection_name: Name for the new collection
        vector_size: Dimension of vectors
        current_user: Current authenticated user (admin only)
        
    Returns:
        Creation status
    """
    try:
        # Admin check
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only admins can create collections")
        
        success = qdrant_service.create_collection(collection_name, vector_size)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create collection")
        
        return {
            "success": True,
            "collection_name": collection_name,
            "vector_size": vector_size
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collection creation failed: {str(e)}")


@router.delete("/collection/{collection_name}")
async def delete_collection(
    collection_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a vector collection (admin only)
    
    Args:
        collection_name: Name of collection to delete
        current_user: Current authenticated user
        
    Returns:
        Deletion status
    """
    try:
        # Admin check
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only admins can delete collections")
        
        success = qdrant_service.delete_collection(collection_name)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete collection")
        
        return {
            "success": True,
            "message": f"Collection '{collection_name}' deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Collection deletion failed: {str(e)}")


@router.get("/health", response_model=VectorHealthResponse)
async def vector_db_health(current_user: User = Depends(get_current_user)):
    """
    Get vector database health status
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Health status of Qdrant service
    """
    try:
        health = qdrant_service.get_health_status()
        return VectorHealthResponse(**health)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.post("/embed-text")
async def embed_text(
    text: str = Query(..., description="Text to embed"),
    current_user: User = Depends(get_current_user)
):
    """
    Generate embedding for a text (for testing)
    
    Args:
        text: Text to generate embedding for
        current_user: Current authenticated user
        
    Returns:
        Embedding vector
    """
    try:
        embedding = await embedding_service.embed_text(text)
        if not embedding:
            raise HTTPException(status_code=400, detail="Failed to generate embedding")
        
        return {
            "success": True,
            "text": text,
            "embedding": embedding,
            "dimension": len(embedding)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")
