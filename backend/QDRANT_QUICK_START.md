# Qdrant Quick Start Guide

## Installation & Setup (5 minutes)

### 1. Verify Prerequisites
```bash
# Check Python
python --version  # Should be 3.10+

# Check if backend is running
curl http://localhost:8000/api/v1/status
```

### 2. Install Dependencies
```bash
cd backend
pip install qdrant-client openai  # Already in requirements.txt
```

### 3. Verify Connection
```bash
# Run verification script
python verify_qdrant.py
```

Expected output:
```
============================================================
Qdrant Vector Database Verification
============================================================

1. Configuration Check:
   - URL: https://d95904a7-0c84-43d2-8df3-15bfd560860a...
   - API Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ...
   - Embedding Model: text-embedding-3-small
   - Embedding Dimension: 1536
   ...

2. Health Status Check:
   - Status: healthy
   - Collections: 2
   - Available Collections: documents, conversations

✅ Verification Complete!
```

## Using Vector Search (10 minutes)

### 1. Search Documents

```bash
# Get authentication token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@acme.com", "password": "SecurePassword123!"}'

# Response: {"access_token": "eyJ...", "token_type": "bearer"}
TOKEN="eyJ..."

# Search documents
curl -X POST http://localhost:8000/api/v1/search/vector-search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning algorithms",
    "limit": 5,
    "score_threshold": 0.7
  }'

# Response:
{
  "success": true,
  "query": "machine learning algorithms",
  "results": [
    {
      "document_id": "doc123",
      "score": 0.92,
      "title": "ML Basics",
      "metadata": {...}
    }
  ],
  "total_results": 1
}
```

### 2. Check Vector Database Health

```bash
curl -X GET http://localhost:8000/api/v1/search/health \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "status": "healthy",
  "collections": 2,
  "models": ["documents", "conversations"]
}
```

### 3. Generate an Embedding (Testing)

```bash
curl -X POST "http://localhost:8000/api/v1/search/embed-text?text=hello%20world" \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "success": true,
  "text": "hello world",
  "embedding": [0.123, 0.456, ...],  # 1536 values
  "dimension": 1536
}
```

## Python Integration Examples

### Example 1: Simple Search

```python
import asyncio
from app.services.qdrant_service import qdrant_service
from app.services.embedding_service import embedding_service

async def search_documents():
    # Generate query embedding
    query = "How to learn Python?"
    query_embedding = await embedding_service.embed_text(query)
    
    # Search
    results = qdrant_service.search_similar(
        collection_name="documents",
        query_vector=query_embedding,
        organization_id="org1",
        limit=5,
        score_threshold=0.7
    )
    
    # Display results
    for result in results:
        print(f"Score: {result['score']:.2f}")
        print(f"Document: {result['document_id']}")
        print(f"Metadata: {result['metadata']}\n")

asyncio.run(search_documents())
```

### Example 2: Index Documents

```python
import asyncio
from app.services.qdrant_service import qdrant_service
from app.services.embedding_service import embedding_service

async def index_documents():
    documents = [
        {
            "id": "doc1",
            "title": "Python Basics",
            "content": "Python is a programming language..."
        },
        {
            "id": "doc2",
            "title": "Advanced Python",
            "content": "Decorators, generators, and async..."
        }
    ]
    
    # Generate embeddings
    texts = [f"{d['title']} {d['content']}" for d in documents]
    embeddings = await embedding_service.embed_texts(texts)
    
    # Prepare batch data
    vectors_data = [
        {
            "id": documents[i]["id"],
            "vector": embeddings[i],
            "metadata": {"title": documents[i]["title"]}
        }
        for i in range(len(documents))
    ]
    
    # Index in batch
    success = qdrant_service.batch_add_vectors(
        collection_name="documents",
        vectors_data=vectors_data,
        organization_id="org1"
    )
    
    print(f"Indexing successful: {success}")

asyncio.run(index_documents())
```

### Example 3: API Endpoint Handler

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.security import get_current_user
from app.services.qdrant_service import qdrant_service
from app.services.embedding_service import embedding_service
from app.models.user import User

router = APIRouter(prefix="/api/v1/custom", tags=["custom"])

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

@router.post("/my-search")
async def my_search(
    request: SearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Custom search endpoint"""
    try:
        # 1. Generate embedding
        embedding = await embedding_service.embed_text(request.query)
        
        if not embedding:
            raise HTTPException(
                status_code=400,
                detail="Failed to generate embedding"
            )
        
        # 2. Search similar documents
        results = qdrant_service.search_similar(
            collection_name="documents",
            query_vector=embedding,
            organization_id=str(current_user.organization_id),
            limit=request.limit
        )
        
        # 3. Return results
        return {
            "success": True,
            "query": request.query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Common Tasks

### Task 1: Create a New Collection

```bash
TOKEN="your_token_here"

curl -X POST "http://localhost:8000/api/v1/search/create-collection" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "articles",
    "vector_size": 1536
  }'
```

### Task 2: List Collections

```bash
curl -X GET http://localhost:8000/api/v1/search/collections \
  -H "Authorization: Bearer $TOKEN"
```

### Task 3: Get Collection Stats

```bash
curl -X GET http://localhost:8000/api/v1/search/collection/documents \
  -H "Authorization: Bearer $TOKEN"
```

### Task 4: Delete Collection (Admin Only)

```bash
curl -X DELETE http://localhost:8000/api/v1/search/collection/test_collection \
  -H "Authorization: Bearer $TOKEN"
```

## Testing with cURL

### Complete Search Example

```bash
#!/bin/bash

# 1. Login and get token
echo "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@acme.com",
    "password": "SecurePassword123!"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token: $TOKEN"

# 2. Perform search
echo "Searching documents..."
curl -X POST http://localhost:8000/api/v1/search/vector-search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "limit": 5,
    "score_threshold": 0.7
  }' | python -m json.tool

# 3. Check health
echo "Checking health..."
curl -X GET http://localhost:8000/api/v1/search/health \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

## Troubleshooting

### Issue: "Service unavailable"
```python
# Check Qdrant service
from app.services.qdrant_service import qdrant_service
health = qdrant_service.get_health_status()
print(health)
```

### Issue: "No results found"
```python
# 1. Check if documents are indexed
from app.services.qdrant_service import qdrant_service

info = qdrant_service.get_collection_info("documents")
print(f"Vectors in collection: {info['points_count']}")

# 2. Lower the threshold
results = qdrant_service.search_similar(
    collection_name="documents",
    query_vector=query_embedding,
    organization_id="org1",
    limit=10,
    score_threshold=0.5  # Lowered from 0.7
)
```

### Issue: "Embedding generation failed"
```python
# Switch to dummy provider for testing
from app.services.embedding_service import EmbeddingService, DummyEmbeddingProvider

service = EmbeddingService(provider=DummyEmbeddingProvider())
```

## API Reference Summary

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/search/vector-search` | POST | Search documents | ✓ |
| `/search/semantic-search` | POST | Custom collection search | ✓ |
| `/search/collection/{name}` | GET | Get collection info | ✓ |
| `/search/collections` | GET | List collections | ✓ |
| `/search/create-collection` | POST | Create collection | ✓ Admin |
| `/search/collection/{name}` | DELETE | Delete collection | ✓ Admin |
| `/search/health` | GET | Health status | ✓ |
| `/search/embed-text` | POST | Generate embedding | ✓ |

## Performance Tips

1. **Batch Operations**: Index multiple documents at once
   ```python
   qdrant_service.batch_add_vectors(
       collection_name="documents",
       vectors_data=[...],  # Multiple vectors
       organization_id="org1"
   )
   ```

2. **Limit Results**: Don't retrieve too many results
   ```python
   results = qdrant_service.search_similar(
       ...,
       limit=10  # Keep reasonable
   )
   ```

3. **Use Thresholds**: Filter low-relevance results
   ```python
   results = qdrant_service.search_similar(
       ...,
       score_threshold=0.75  # Higher = more relevant
   )
   ```

4. **Batch Searches**: Use batch operations for multiple queries
   ```python
   queries = ["query1", "query2", "query3"]
   embeddings = await embedding_service.embed_texts(queries)
   # Search each in parallel
   ```

## Next Steps

1. **Read Documentation**
   - `QDRANT_INTEGRATION.md` - Complete guide
   - `QDRANT_ARCHITECTURE.md` - System design

2. **Integrate with Your Code**
   - Add vector search to document endpoints
   - Index documents on creation
   - Add semantic search to UI

3. **Run Tests**
   ```bash
   pytest tests/test_qdrant_integration.py -v
   ```

4. **Monitor Performance**
   - Check search latency
   - Monitor collection size
   - Track embedding costs

---

**Need Help?**
- Check logs: `backend/logs/`
- Run diagnostics: `python verify_qdrant.py`
- Review examples: `tests/test_qdrant_integration.py`
