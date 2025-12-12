"""
Qdrant Vector Database Service
Handles vector embeddings, storage, and similarity search
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, PointStruct, VectorParams, FieldCondition, 
    MatchValue, Filter, HasIdCondition, PointIdsList
)

from app.config.qdrant_config import qdrant_config

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for managing vector operations with Qdrant"""
    
    def __init__(self):
        """Initialize Qdrant client with cloud configuration"""
        try:
            self.client = QdrantClient(
                url=qdrant_config.qdrant_url,
                api_key=qdrant_config.qdrant_api_key
            )
            self.embedding_dimension = qdrant_config.embedding_dimension
            self.similarity_threshold = qdrant_config.similarity_threshold
            self.max_search_results = qdrant_config.max_search_results
            
            logger.info("Qdrant client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {str(e)}")
            raise
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Qdrant service health status"""
        try:
            info = self.client.get_collections()
            return {
                "status": "healthy",
                "collections": len(info.collections),
                "models": [col.name for col in info.collections]
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def create_collection(self, collection_name: str, vector_size: Optional[int] = None) -> bool:
        """
        Create a new collection if it doesn't exist
        
        Args:
            collection_name: Name of the collection
            vector_size: Dimension of vectors (defaults to embedding_dimension)
            
        Returns:
            True if created or already exists, False on error
        """
        try:
            vector_size = vector_size or self.embedding_dimension
            
            # Check if collection exists
            collections = self.client.get_collections()
            if any(col.name == collection_name for col in collections.collections):
                logger.info(f"Collection '{collection_name}' already exists")
                return True
            
            # Create new collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                ),
                optimizers_config={
                    "default_segment_number": 2,
                    "min_segment_number": 1,
                    "max_segment_number": 4,
                    "inactive_segment_number": 1,
                    "inactive_collection_threshold": 20000,
                    "active_collection_threshold": 20000,
                    "segment_number_limit": 4,
                    "snapshots_path": None,
                    "indexing_threshold": 20000,
                    "flush_interval_sec": 10,
                    "max_optimization_threads": 1,
                }
            )
            
            logger.info(f"Collection '{collection_name}' created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating collection '{collection_name}': {str(e)}")
            return False
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Collection '{collection_name}' deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection '{collection_name}': {str(e)}")
            return False
    
    def add_document_vector(
        self,
        collection_name: str,
        document_id: str,
        vector: List[float],
        metadata: Dict[str, Any],
        organization_id: str,
        project_id: Optional[str] = None
    ) -> bool:
        """
        Add a document vector to the collection
        
        Args:
            collection_name: Target collection
            document_id: Document identifier
            vector: Embedding vector
            metadata: Document metadata
            organization_id: Organization owning the document
            project_id: Optional project identifier
            
        Returns:
            True if successful, False on error
        """
        try:
            # Ensure collection exists
            self.create_collection(collection_name)
            
            # Prepare point with metadata payload
            point = PointStruct(
                id=hash(f"{organization_id}_{document_id}") & 0x7fffffff,  # Use positive hash
                vector=vector,
                payload={
                    "document_id": document_id,
                    "organization_id": organization_id,
                    "project_id": project_id,
                    "created_at": datetime.utcnow().isoformat(),
                    **metadata  # Include all metadata
                }
            )
            
            # Upsert the point
            self.client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
            logger.info(f"Document vector added to '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error adding document vector: {str(e)}")
            return False
    
    def search_similar(
        self,
        collection_name: str,
        query_vector: List[float],
        organization_id: str,
        limit: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity
        
        Args:
            collection_name: Collection to search
            query_vector: Query embedding vector
            organization_id: Filter by organization
            limit: Max number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of similar documents with scores
        """
        try:
            limit = limit or self.max_search_results
            score_threshold = score_threshold or self.similarity_threshold
            
            # Create filter for organization
            org_filter = Filter(
                must=[
                    FieldCondition(
                        key="organization_id",
                        match=MatchValue(value=organization_id)
                    )
                ]
            )
            
            # Perform search
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=org_filter,
                score_threshold=score_threshold
            )
            
            # Format results
            formatted_results = [
                {
                    "score": result.score,
                    "document_id": result.payload.get("document_id"),
                    "organization_id": result.payload.get("organization_id"),
                    "project_id": result.payload.get("project_id"),
                    "metadata": {k: v for k, v in result.payload.items() 
                                 if k not in ["document_id", "organization_id", "project_id"]}
                }
                for result in results
            ]
            
            logger.info(f"Found {len(formatted_results)} similar documents")
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching similar documents: {str(e)}")
            return []
    
    def delete_document_vector(
        self,
        collection_name: str,
        document_id: str,
        organization_id: str
    ) -> bool:
        """
        Delete a document vector from the collection
        
        Args:
            collection_name: Target collection
            document_id: Document to delete
            organization_id: Organization owning the document
            
        Returns:
            True if successful, False on error
        """
        try:
            # Create filter for the document
            doc_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    ),
                    FieldCondition(
                        key="organization_id",
                        match=MatchValue(value=organization_id)
                    )
                ]
            )
            
            # Delete matching points
            self.client.delete(
                collection_name=collection_name,
                points_selector=doc_filter
            )
            
            logger.info(f"Document vector deleted from '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting document vector: {str(e)}")
            return False
    
    def update_document_vector(
        self,
        collection_name: str,
        document_id: str,
        vector: List[float],
        metadata: Dict[str, Any],
        organization_id: str,
        project_id: Optional[str] = None
    ) -> bool:
        """
        Update a document vector
        
        Args:
            collection_name: Target collection
            document_id: Document to update
            vector: New embedding vector
            metadata: Updated metadata
            organization_id: Organization owning the document
            project_id: Optional project identifier
            
        Returns:
            True if successful, False on error
        """
        # Delete old vector and add updated one
        if not self.delete_document_vector(collection_name, document_id, organization_id):
            return False
        
        return self.add_document_vector(
            collection_name, document_id, vector, metadata, organization_id, project_id
        )
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a collection"""
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
                "disk_data_size": info.disk_data_size,
                "disk_index_size": info.disk_index_size
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return None
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        try:
            collections = self.client.get_collections()
            return [col.name for col in collections.collections]
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            return []
    
    def batch_add_vectors(
        self,
        collection_name: str,
        vectors_data: List[Dict[str, Any]],
        organization_id: str
    ) -> bool:
        """
        Add multiple vectors in batch
        
        Args:
            collection_name: Target collection
            vectors_data: List of {"id", "vector", "metadata"} dicts
            organization_id: Organization owning the documents
            
        Returns:
            True if successful, False on error
        """
        try:
            self.create_collection(collection_name)
            
            points = [
                PointStruct(
                    id=hash(f"{organization_id}_{v['id']}") & 0x7fffffff,
                    vector=v['vector'],
                    payload={
                        "document_id": v['id'],
                        "organization_id": organization_id,
                        "created_at": datetime.utcnow().isoformat(),
                        **v.get('metadata', {})
                    }
                )
                for v in vectors_data
            ]
            
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"Added {len(points)} vectors to '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error batch adding vectors: {str(e)}")
            return False


# Create global Qdrant service instance
qdrant_service = QdrantService()
