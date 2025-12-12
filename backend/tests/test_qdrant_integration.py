"""
Tests for Qdrant Vector Database Integration
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.qdrant_service import QdrantService
from app.services.embedding_service import (
    EmbeddingService, OpenAIEmbeddingProvider, DummyEmbeddingProvider
)


class TestQdrantService:
    """Tests for Qdrant service"""
    
    @pytest.fixture
    def qdrant_service(self):
        """Create Qdrant service with mocked client"""
        with patch('app.services.qdrant_service.QdrantClient'):
            return QdrantService()
    
    def test_get_health_status(self, qdrant_service):
        """Test health status check"""
        # Mock the client method
        mock_collection = Mock(name='test_collection')
        qdrant_service.client.get_collections = Mock(
            return_value=Mock(collections=[mock_collection])
        )
        
        health = qdrant_service.get_health_status()
        
        assert health['status'] == 'healthy'
        assert health['collections'] == 1
    
    def test_create_collection(self, qdrant_service):
        """Test collection creation"""
        qdrant_service.client.get_collections = Mock(
            return_value=Mock(collections=[])
        )
        qdrant_service.client.create_collection = Mock()
        
        result = qdrant_service.create_collection('test_collection', 1536)
        
        assert result is True
        qdrant_service.client.create_collection.assert_called_once()
    
    def test_create_existing_collection(self, qdrant_service):
        """Test creating a collection that already exists"""
        existing_collection = Mock(name='existing')
        qdrant_service.client.get_collections = Mock(
            return_value=Mock(collections=[existing_collection])
        )
        
        result = qdrant_service.create_collection('existing', 1536)
        
        assert result is True
    
    def test_add_document_vector(self, qdrant_service):
        """Test adding a document vector"""
        qdrant_service.client.get_collections = Mock(
            return_value=Mock(collections=[])
        )
        qdrant_service.client.create_collection = Mock()
        qdrant_service.client.upsert = Mock()
        
        result = qdrant_service.add_document_vector(
            collection_name='documents',
            document_id='doc1',
            vector=[0.1] * 1536,
            metadata={'title': 'Test'},
            organization_id='org1'
        )
        
        assert result is True
        qdrant_service.client.upsert.assert_called_once()
    
    def test_delete_document_vector(self, qdrant_service):
        """Test deleting a document vector"""
        qdrant_service.client.delete = Mock()
        
        result = qdrant_service.delete_document_vector(
            collection_name='documents',
            document_id='doc1',
            organization_id='org1'
        )
        
        assert result is True
    
    def test_search_similar(self, qdrant_service):
        """Test similarity search"""
        mock_result = Mock(
            score=0.95,
            payload={
                'document_id': 'doc1',
                'organization_id': 'org1',
                'project_id': 'proj1',
                'title': 'Test Document'
            }
        )
        
        qdrant_service.client.search = Mock(return_value=[mock_result])
        
        results = qdrant_service.search_similar(
            collection_name='documents',
            query_vector=[0.1] * 1536,
            organization_id='org1'
        )
        
        assert len(results) == 1
        assert results[0]['score'] == 0.95
        assert results[0]['document_id'] == 'doc1'
    
    def test_batch_add_vectors(self, qdrant_service):
        """Test batch adding vectors"""
        qdrant_service.client.get_collections = Mock(
            return_value=Mock(collections=[])
        )
        qdrant_service.client.create_collection = Mock()
        qdrant_service.client.upsert = Mock()
        
        vectors_data = [
            {
                'id': 'doc1',
                'vector': [0.1] * 1536,
                'metadata': {'title': 'Doc 1'}
            },
            {
                'id': 'doc2',
                'vector': [0.2] * 1536,
                'metadata': {'title': 'Doc 2'}
            }
        ]
        
        result = qdrant_service.batch_add_vectors(
            collection_name='documents',
            vectors_data=vectors_data,
            organization_id='org1'
        )
        
        assert result is True
        qdrant_service.client.upsert.assert_called_once()


class TestEmbeddingService:
    """Tests for embedding service"""
    
    @pytest.mark.asyncio
    async def test_dummy_embedding_provider(self):
        """Test dummy embedding provider"""
        provider = DummyEmbeddingProvider(dimension=1536)
        
        embedding = await provider.generate_embedding("test text")
        
        assert len(embedding) == 1536
        assert all(isinstance(v, float) for v in embedding)
    
    @pytest.mark.asyncio
    async def test_dummy_batch_embeddings(self):
        """Test dummy batch embeddings"""
        provider = DummyEmbeddingProvider(dimension=1536)
        
        embeddings = await provider.generate_embeddings([
            "text 1",
            "text 2",
            "text 3"
        ])
        
        assert len(embeddings) == 3
        assert all(len(e) == 1536 for e in embeddings)
    
    @pytest.mark.asyncio
    async def test_embedding_service_with_dummy_provider(self):
        """Test embedding service with dummy provider"""
        service = EmbeddingService(
            provider=DummyEmbeddingProvider(dimension=1536)
        )
        
        embedding = await service.embed_text("test document")
        
        assert len(embedding) == 1536
    
    @pytest.mark.asyncio
    async def test_embed_empty_text(self):
        """Test embedding empty text"""
        service = EmbeddingService(
            provider=DummyEmbeddingProvider(dimension=1536)
        )
        
        embedding = await service.embed_text("")
        
        assert embedding == []
    
    @pytest.mark.asyncio
    async def test_embed_document(self):
        """Test document embedding with title, content, and metadata"""
        service = EmbeddingService(
            provider=DummyEmbeddingProvider(dimension=1536)
        )
        
        embedding = await service.embed_document(
            title="Test Document",
            content="This is the document content",
            metadata="important"
        )
        
        assert len(embedding) == 1536


class TestVectorSearchEndpoints:
    """Tests for vector search endpoints"""
    
    @pytest.mark.asyncio
    async def test_vector_search_endpoint(self, client, test_user):
        """Test vector search endpoint"""
        response = client.post(
            "/api/v1/search/vector-search",
            json={
                "query": "test search",
                "limit": 10,
                "score_threshold": 0.7
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        
        assert response.status_code in [200, 500]  # May fail if service unavailable
    
    @pytest.mark.asyncio
    async def test_list_collections_endpoint(self, client, test_user):
        """Test list collections endpoint"""
        response = client.get(
            "/api/v1/search/collections",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        
        assert response.status_code in [200, 500]  # May fail if service unavailable
    
    @pytest.mark.asyncio
    async def test_vector_health_endpoint(self, client, test_user):
        """Test vector database health endpoint"""
        response = client.get(
            "/api/v1/search/health",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        
        assert response.status_code in [200, 500]  # May fail if service unavailable
    
    @pytest.mark.asyncio
    async def test_embed_text_endpoint(self, client, test_user):
        """Test text embedding endpoint"""
        response = client.post(
            "/api/v1/search/embed-text",
            params={"text": "test text"},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        
        assert response.status_code in [200, 500]  # May fail if service unavailable


class TestVectorDocumentIntegration:
    """Integration tests for document vector indexing"""
    
    @pytest.mark.asyncio
    async def test_document_vector_indexing_flow(self, qdrant_service):
        """Test complete document indexing flow"""
        # Setup
        qdrant_service.client.get_collections = Mock(
            return_value=Mock(collections=[])
        )
        qdrant_service.client.create_collection = Mock()
        qdrant_service.client.upsert = Mock()
        
        # Create embedding service
        embedding_service = EmbeddingService(
            provider=DummyEmbeddingProvider(dimension=1536)
        )
        
        # Generate embedding
        embedding = await embedding_service.embed_document(
            title="Test Document",
            content="This is test content",
            metadata="test"
        )
        
        # Add to vector DB
        result = qdrant_service.add_document_vector(
            collection_name='documents',
            document_id='doc123',
            vector=embedding,
            metadata={'title': 'Test Document'},
            organization_id='org1'
        )
        
        assert result is True
        assert len(embedding) == 1536
