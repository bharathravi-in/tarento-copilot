# Qdrant Vector Database Integration Guide

## Overview

This document provides a comprehensive guide to the Qdrant vector database integration in the Tarento Copilot backend. Qdrant is used for semantic search, similarity matching, and vector-based document indexing.

## Configuration

### Environment Setup

Qdrant configuration is stored in `app/config/qdrant_config.py`:

```python
QDRANT_URL="https://d95904a7-0c84-43d2-8df3-15bfd560860a.europe-west3-0.gcp.cloud.qdrant.io:6333"
QDRANT_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.L5gEpZCjcAY94zC_lSlZq-1KuKGLvxXwrThrO3rNdOw"
```

The configuration includes:
- **qdrant_url**: Cloud Qdrant instance URL
- **qdrant_api_key**: API authentication key
- **embedding_model**: OpenAI text-embedding-3-small
- **embedding_dimension**: 1536 (standard for text-embedding-3-small)
- **document_collection**: "documents" (primary collection)
- **conversation_collection**: "conversations" (for conversation history)
- **similarity_threshold**: 0.7 (minimum relevance score)

## Core Services

### 1. Qdrant Service (`app/services/qdrant_service.py`)

Main service for vector database operations:

```python
from app.services.qdrant_service import qdrant_service

# Collection Management
qdrant_service.create_collection("documents", vector_size=1536)
qdrant_service.delete_collection("documents")
qdrant_service.list_collections()

# Document Vectors
qdrant_service.add_document_vector(
    collection_name="documents",
    document_id="doc123",
    vector=[...],  # 1536-dim vector
    metadata={"title": "Document Title"},
    organization_id="org1"
)

# Search Operations
results = qdrant_service.search_similar(
    collection_name="documents",
    query_vector=[...],
    organization_id="org1",
    limit=10,
    score_threshold=0.7
)

# Batch Operations
qdrant_service.batch_add_vectors(
    collection_name="documents",
    vectors_data=[
        {"id": "doc1", "vector": [...], "metadata": {...}},
        {"id": "doc2", "vector": [...], "metadata": {...}}
    ],
    organization_id="org1"
)
```

**Key Methods:**

| Method | Purpose |
|--------|---------|
| `create_collection()` | Create or verify collection exists |
| `delete_collection()` | Remove a collection |
| `add_document_vector()` | Add/update single document vector |
| `batch_add_vectors()` | Add multiple vectors efficiently |
| `delete_document_vector()` | Remove document from index |
| `update_document_vector()` | Update existing document vector |
| `search_similar()` | Find similar documents by vector |
| `get_collection_info()` | Get collection statistics |
| `list_collections()` | List all collections |
| `get_health_status()` | Check service health |

### 2. Embedding Service (`app/services/embedding_service.py`)

Generates vector embeddings for text:

```python
from app.services.embedding_service import embedding_service

# Single text embedding
embedding = await embedding_service.embed_text("search query")

# Multiple texts (batch)
embeddings = await embedding_service.embed_texts([
    "text 1",
    "text 2",
    "text 3"
])

# Document embedding (combines title, content, metadata)
embedding = await embedding_service.embed_document(
    title="Document Title",
    content="Document content...",
    metadata="additional metadata"
)
```

**Embedding Providers:**

1. **OpenAIEmbeddingProvider** (Primary)
   - Model: text-embedding-3-small
   - Dimension: 1536
   - Requires: OPENAI_API_KEY environment variable

2. **DummyEmbeddingProvider** (Fallback/Testing)
   - Generates random vectors
   - Useful for testing without API calls

## API Endpoints

### Vector Search Endpoints

**Base URL**: `/api/v1/search`

#### 1. Vector Search
```http
POST /vector-search
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": "search term",
  "limit": 10,
  "score_threshold": 0.7
}

Response:
{
  "success": true,
  "query": "search term",
  "results": [
    {
      "document_id": "doc123",
      "score": 0.95,
      "title": "Document Title",
      "metadata": {...}
    }
  ],
  "total_results": 1
}
```

#### 2. Semantic Search
```http
POST /semantic-search
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": "semantic query",
  "collection": "documents",
  "limit": 10,
  "min_score": 0.7
}
```

#### 3. Get Collection Info
```http
GET /collection/{collection_name}
Authorization: Bearer <token>

Response:
{
  "name": "documents",
  "points_count": 1000,
  "vectors_count": 1000,
  "disk_data_size": 5242880,
  "disk_index_size": 2097152
}
```

#### 4. List Collections
```http
GET /collections
Authorization: Bearer <token>

Response:
{
  "collections": ["documents", "conversations"],
  "total": 2
}
```

#### 5. Create Collection (Admin)
```http
POST /create-collection
Authorization: Bearer <token>

Query Parameters:
- collection_name: string (required)
- vector_size: integer (optional, default: 1536)

Response:
{
  "success": true,
  "collection_name": "documents",
  "vector_size": 1536
}
```

#### 6. Delete Collection (Admin)
```http
DELETE /collection/{collection_name}
Authorization: Bearer <token>

Response:
{
  "success": true,
  "message": "Collection 'documents' deleted"
}
```

#### 7. Vector Database Health
```http
GET /health
Authorization: Bearer <token>

Response:
{
  "status": "healthy",
  "collections": 2,
  "models": ["documents", "conversations"]
}
```

#### 8. Embed Text (Testing)
```http
POST /embed-text
Authorization: Bearer <token>

Query Parameters:
- text: string (required)

Response:
{
  "success": true,
  "text": "input text",
  "embedding": [0.1, 0.2, ...],
  "dimension": 1536
}
```

## Usage Examples

### Document Indexing Workflow

```python
# 1. Generate embedding for document
from app.services.embedding_service import embedding_service
from app.services.qdrant_service import qdrant_service

document = {
    "id": "doc123",
    "title": "Machine Learning Basics",
    "content": "Machine learning is...",
    "organization_id": "org1"
}

# Generate vector
embedding = await embedding_service.embed_document(
    title=document["title"],
    content=document["content"],
    metadata="tutorial"
)

# Add to vector DB
qdrant_service.add_document_vector(
    collection_name="documents",
    document_id=document["id"],
    vector=embedding,
    metadata={"title": document["title"], "type": "tutorial"},
    organization_id=document["organization_id"]
)
```

### Search Workflow

```python
# 1. Get query embedding
query = "How does machine learning work?"
query_embedding = await embedding_service.embed_text(query)

# 2. Search for similar documents
results = qdrant_service.search_similar(
    collection_name="documents",
    query_vector=query_embedding,
    organization_id="org1",
    limit=5,
    score_threshold=0.75
)

# 3. Results are ranked by similarity
for result in results:
    print(f"Score: {result['score']}, Doc: {result['document_id']}")
```

### Multi-tenant Organization Scoping

All search operations automatically filter by organization:

```python
# This will ONLY return documents from the current user's organization
results = qdrant_service.search_similar(
    collection_name="documents",
    query_vector=query_embedding,
    organization_id=current_user.organization_id,  # Automatic scoping
    limit=10
)
```

## Collections

### Predefined Collections

1. **documents**
   - Purpose: Document semantic search
   - Vector Size: 1536
   - Distance Metric: Cosine similarity
   - Payload Fields: document_id, organization_id, project_id, title, type, created_at

2. **conversations**
   - Purpose: Conversation history and context retrieval
   - Vector Size: 1536
   - Distance Metric: Cosine similarity
   - Payload Fields: message_id, conversation_id, organization_id, role, created_at

## Testing

### Running Tests

```bash
# All Qdrant tests
pytest tests/test_qdrant_integration.py -v

# Specific test
pytest tests/test_qdrant_integration.py::TestQdrantService::test_search_similar -v

# With coverage
pytest tests/test_qdrant_integration.py --cov=app.services --cov-report=html
```

### Test Coverage

1. **Service Tests**
   - Collection creation/deletion
   - Vector addition/deletion/updating
   - Similarity search
   - Batch operations
   - Health checks

2. **Embedding Tests**
   - Dummy provider
   - OpenAI provider (mocked)
   - Batch embeddings
   - Document embeddings

3. **Endpoint Tests**
   - Vector search endpoint
   - Collection management
   - Health endpoint
   - Embedding generation

4. **Integration Tests**
   - Full document indexing flow
   - Search and retrieval
   - Organization scoping

## Performance Optimization

### Indexing Optimization

```python
# Batch add large numbers of vectors
vectors_data = [
    {
        "id": f"doc{i}",
        "vector": embeddings[i],
        "metadata": metadata[i]
    }
    for i in range(1000)
]

qdrant_service.batch_add_vectors(
    collection_name="documents",
    vectors_data=vectors_data,
    organization_id="org1"
)
```

### Search Optimization

```python
# Use appropriate thresholds
results = qdrant_service.search_similar(
    collection_name="documents",
    query_vector=query_embedding,
    organization_id="org1",
    limit=10,           # Limit results
    score_threshold=0.75  # Filter low-confidence matches
)
```

### Collection Optimization

Qdrant configuration includes:
- Segment optimization for fast searches
- Index optimization for memory efficiency
- Snapshot configuration for durability
- Flush interval optimization for consistency

## Error Handling

All operations include comprehensive error handling:

```python
try:
    results = qdrant_service.search_similar(...)
except Exception as e:
    logger.error(f"Search failed: {str(e)}")
    return []
```

API endpoints return appropriate HTTP status codes:
- 200: Success
- 400: Invalid request/parameters
- 403: Insufficient permissions
- 404: Resource not found
- 500: Server error

## Troubleshooting

### Connection Issues

```python
health = qdrant_service.get_health_status()
if health['status'] != 'healthy':
    print(f"Error: {health.get('error')}")
```

### Embedding Failures

Fallback to dummy provider for testing:

```python
from app.services.embedding_service import DummyEmbeddingProvider, EmbeddingService

service = EmbeddingService(provider=DummyEmbeddingProvider())
```

### Search Returns No Results

Check:
1. Collection exists: `qdrant_service.list_collections()`
2. Documents indexed: `qdrant_service.get_collection_info("documents")`
3. Threshold not too high: Try `score_threshold=0.5`
4. Organization filter: Verify organization_id matches

## Next Steps

- Integrate with document upload pipeline
- Add vector indexing on document creation
- Implement semantic caching with Redis
- Add vector search to document API
- Build RAG (Retrieval-Augmented Generation) pipeline
- Implement vector search in conversations module
