# Qdrant Integration with Tarento Copilot - Technical Architecture

## System Overview

The Qdrant vector database integration extends Tarento Copilot with semantic search capabilities, enabling intelligent document retrieval and similarity matching across the enterprise AI co-pilot platform.

```
┌────────────────────────────────────────────────────────────────────┐
│                        Frontend (React + TypeScript)               │
│                     - Search UI Component                          │
│                     - Results Display                              │
│                     - Semantic Query Interface                     │
└────────────────────────┬───────────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼───────────────────────────────────────────┐
│                   FastAPI Backend (Python)                         │
├────────────────────────────────────────────────────────────────────┤
│  REST API Endpoints                                                │
│  ├─ /api/v1/auth/*           [Authentication]                     │
│  ├─ /api/v1/users/*          [User Management]                    │
│  ├─ /api/v1/organizations/*  [Organization Management]            │
│  ├─ /api/v1/projects/*       [Project Management]                 │
│  ├─ /api/v1/documents/*      [Document CRUD]                      │
│  ├─ /api/v1/conversations/*  [Conversation Management]            │
│  └─ /api/v1/search/*         [Vector Search] ◄─── NEW             │
├────────────────────────────────────────────────────────────────────┤
│  Application Services                                              │
│  ├─ qdrant_service.py        [Vector DB Operations]              │
│  ├─ embedding_service.py     [Vector Generation]                 │
│  ├─ security.py              [Authentication]                     │
│  ├─ google_adk_service.py    [Agent Management]                  │
│  └─ ... (other services)                                          │
├────────────────────────────────────────────────────────────────────┤
│  Data Layer                                                        │
│  ├─ SQLAlchemy ORM            [PostgreSQL Models]                │
│  │  ├─ Document Model                                            │
│  │  ├─ Conversation Model                                        │
│  │  └─ ... (11 total tables)                                     │
│  │                                                                │
│  └─ Vector Indexing                                              │
│     ├─ Document → Embedding → Qdrant                            │
│     └─ Message → Embedding → Qdrant                             │
└────────────────────────┬───────────────────────────────────────────┘
                         │ Network/API
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐ ┌──────▼─────┐ ┌────────▼──────┐
│ PostgreSQL   │ │  Qdrant    │ │ OpenAI API   │
│              │ │  Cloud VDB │ │              │
│ - Database   │ │            │ │ - Embeddings │
│ - 11 Tables  │ │ Collections│ │ - LLM Calls  │
│ - Indexes    │ │ - documents│ │              │
│ - Relations  │ │ - conversat│ │              │
└──────────────┘ └────────────┘ └──────────────┘
```

## Data Flow - Document Indexing

```
1. Document Creation
   ┌─────────────────────────┐
   │ POST /documents         │
   │ {                       │
   │   "title": "...",       │
   │   "content": "...",     │
   │   "org_id": "org1"      │
   │ }                       │
   └────────┬────────────────┘
            │
            ▼
   ┌─────────────────────────┐
   │ Store in PostgreSQL     │ ◄─── Document Model
   │ document_id: "doc123"   │
   └────────┬────────────────┘
            │
            ▼
   ┌─────────────────────────┐
   │ Generate Embedding      │ ◄─── EmbeddingService
   │ OpenAI API Call        │
   │ Returns 1536-dim vector │
   └────────┬────────────────┘
            │
            ▼
   ┌─────────────────────────┐
   │ Index in Qdrant        │ ◄─── QdrantService
   │ Collection: "documents" │
   │ Payload metadata        │
   └────────┬────────────────┘
            │
            ▼
   ┌─────────────────────────┐
   │ Return Document         │
   │ with vector_indexed:true│
   └─────────────────────────┘
```

## Data Flow - Semantic Search

```
1. User Search Query
   ┌──────────────────────────┐
   │ POST /search/            │
   │ vector-search           │
   │ {                        │
   │   "query": "How does...",│
   │   "limit": 10            │
   │ }                        │
   └────────┬─────────────────┘
            │
            ▼
   ┌──────────────────────────┐
   │ Extract & Validate       │
   │ - Current User           │
   │ - Organization ID        │
   │ - Query String           │
   └────────┬─────────────────┘
            │
            ▼
   ┌──────────────────────────┐
   │ Generate Query Embedding │ ◄─── EmbeddingService
   │ "How does..." → [...]    │      OpenAI API
   │ 1536 dimensions          │
   └────────┬─────────────────┘
            │
            ▼
   ┌──────────────────────────┐
   │ Search Similar Vectors   │ ◄─── QdrantService
   │ - Collection: documents  │      Cosine Similarity
   │ - Filter: org_id = org1  │
   │ - Threshold: 0.7         │
   │ - Limit: 10              │
   └────────┬─────────────────┘
            │
            ▼
   ┌──────────────────────────┐
   │ Get Document Details     │ ◄─── PostgreSQL
   │ from PostgreSQL using    │
   │ document_ids from results│
   └────────┬─────────────────┘
            │
            ▼
   ┌──────────────────────────┐
   │ Return Ranked Results    │
   │ [                        │
   │   {                      │
   │     "score": 0.95,       │
   │     "document": {...}    │
   │   },                     │
   │   ...                    │
   │ ]                        │
   └──────────────────────────┘
```

## Multi-tenancy Architecture

All vector operations are automatically scoped by organization:

```
Organization A                    Organization B
─────────────────────────────────────────────────

PostgreSQL                        PostgreSQL
├─ users (org_a only)            ├─ users (org_b only)
├─ documents                      ├─ documents
│  ├─ doc1 (org_a)               │  ├─ doc1 (org_b)
│  └─ doc2 (org_a)               │  └─ doc2 (org_b)
└─ conversations                  └─ conversations

Qdrant "documents" Collection      Qdrant "documents" Collection
─────────────────────────────     ─────────────────────────────

Vector 1: doc1                    Vector 1: doc1
{                                 {
  org_id: "org_a",                org_id: "org_b",
  doc_id: "doc1",                 doc_id: "doc1",
  title: "Doc A1"                 title: "Doc B1"
}                                 }

Vector 2: doc2                    Vector 2: doc2
{                                 {
  org_id: "org_a",                org_id: "org_b",
  doc_id: "doc2",                 doc_id: "doc2",
  title: "Doc A2"                 title: "Doc B2"
}                                 }

Search Filter:
org_id == "org_a"                Search Filter:
│                                org_id == "org_b"
├─ Only doc1, doc2 visible       │
│                                ├─ Only doc1, doc2 visible
└─ org_b documents hidden        │
                                 └─ org_a documents hidden
```

## Authentication & Authorization

```
HTTP Request
    │
    ├─ /api/v1/search/vector-search
    │  Authorization: Bearer <JWT_TOKEN>
    │
    ▼
Dependency: get_current_user()
    │
    ├─ Extract & Verify JWT
    ├─ Load User from DB
    └─ Return User object
       │
       ├─ user_id
       ├─ organization_id ◄─── Used for filtering
       ├─ is_superuser
       └─ permissions
       
    ▼
Endpoint Handler
    │
    ├─ Receives current_user
    ├─ Extracts organization_id
    └─ Passes to service with org filter
    
    ▼
QdrantService.search_similar()
    │
    ├─ Creates filter:
    │  {
    │    "must": [
    │      { "key": "organization_id", "match": organization_id }
    │    ]
    │  }
    │
    └─ Only returns org's vectors
```

## Collection Schema

### Documents Collection
```python
Collection Name: "documents"
Vector Dimension: 1536 (OpenAI text-embedding-3-small)
Distance Metric: Cosine Similarity

Point Structure:
{
  "id": hash(org_id + document_id),  # Unique point ID
  "vector": [1536 floats],           # Embedding vector
  "payload": {
    "document_id": "doc123",
    "organization_id": "org1",
    "project_id": "proj1",           # Optional
    "title": "Document Title",       # From metadata
    "type": "pdf|docx|txt|...",     # Document type
    "created_at": "2024-01-01T...",
    "custom_field": "value"          # Any additional metadata
  }
}

Indexes:
- document_id (indexed for filtering)
- organization_id (indexed for multi-tenancy)
- created_at (indexed for sorting)
```

### Conversations Collection
```python
Collection Name: "conversations"
Vector Dimension: 1536
Distance Metric: Cosine Similarity

Point Structure:
{
  "id": hash(org_id + message_id),
  "vector": [1536 floats],
  "payload": {
    "message_id": "msg123",
    "conversation_id": "conv123",
    "organization_id": "org1",
    "role": "user|assistant",        # Message role
    "content": "Message content",    # Message text
    "created_at": "2024-01-01T...",
    "metadata": {}
  }
}
```

## Error Handling & Recovery

```
Vector Operation
    │
    ├─ Try: Execute operation
    │
    ├─ Catch: ConnectionError
    │  └─ Log error
    │  └─ Return {status: 500, error: "DB connection failed"}
    │
    ├─ Catch: EmbeddingError
    │  └─ Log error
    │  └─ Fallback to dummy provider OR return 400
    │
    ├─ Catch: ValidationError
    │  └─ Log error
    │  └─ Return {status: 400, error: "Invalid parameters"}
    │
    └─ Success
       └─ Return results
```

## Performance Considerations

### Query Optimization
1. **Index Strategy**
   - organization_id: Indexed (filtering)
   - document_id: Indexed (lookups)
   - created_at: Indexed (sorting)

2. **Vector Search Optimization**
   - Limit results (default: 10, max: 100)
   - Use appropriate score threshold (default: 0.7)
   - Organization filter reduces search space
   - Batch operations when indexing multiple documents

3. **Caching Strategy**
   - Query embeddings can be cached (same query = same embedding)
   - Document metadata cached in PostgreSQL
   - Vector DB handles internal caching

### Scaling Strategy
```
Current:
- Single Qdrant cloud instance
- Multiple collections (documents, conversations, etc.)
- Organization-level sharding in payload

Future (if needed):
- Separate Qdrant instances per organization
- Dedicated vector search workers
- Redis caching layer
- Embedding cache (Redis)
```

## Integration with Existing Modules

### Document Module Integration
```python
# In documents.py POST endpoint
@router.post("/documents/")
async def create_document(...):
    # 1. Create document in PostgreSQL
    db_document = Document(...)
    db.add(db_document)
    db.commit()
    
    # 2. Generate embedding
    embedding = await embedding_service.embed_document(
        title=db_document.title,
        content=db_document.content,
        metadata=db_document.metadata
    )
    
    # 3. Index in Qdrant
    qdrant_service.add_document_vector(
        collection_name="documents",
        document_id=str(db_document.id),
        vector=embedding,
        metadata={"title": db_document.title},
        organization_id=str(current_user.organization_id)
    )
    
    return DocumentResponse(...)
```

### Conversation Module Integration
```python
# In conversations.py message creation
@router.post("/conversations/{conv_id}/messages")
async def add_message(...):
    # 1. Store message in PostgreSQL
    message = Message(...)
    db.add(message)
    db.commit()
    
    # 2. Index message embedding for context retrieval
    if include_in_search:
        embedding = await embedding_service.embed_text(message.content)
        qdrant_service.add_document_vector(
            collection_name="conversations",
            document_id=str(message.id),
            vector=embedding,
            metadata={"conversation_id": str(conv_id)},
            organization_id=str(current_user.organization_id)
        )
    
    return MessageResponse(...)
```

### Agent Module Integration (RAG Pipeline)
```python
# In agents.py - Retrieval Augmented Generation
@router.post("/agents/execute-rag")
async def execute_rag(request: RagExecuteRequest, ...):
    # 1. Generate query embedding
    query_embedding = await embedding_service.embed_text(request.user_input)
    
    # 2. Retrieve relevant documents
    context_docs = qdrant_service.search_similar(
        collection_name="documents",
        query_vector=query_embedding,
        organization_id=str(current_user.organization_id),
        limit=5
    )
    
    # 3. Build context from retrieved documents
    context = "\n".join([d['metadata'].get('content') for d in context_docs])
    
    # 4. Generate response with context
    response = await google_adk_service.execute_agent(
        context=AgentContext(...),
        user_input=request.user_input,
        system_prompt=f"Context:\n{context}\n\nUser query: {request.user_input}"
    )
    
    return response
```

## Testing Strategy

### Unit Tests
- Service methods (QdrantService, EmbeddingService)
- Provider implementations
- Error handling

### Integration Tests
- Full indexing pipeline (create document → index vector)
- Search flow (query → embedding → search → results)
- Multi-tenancy isolation

### Endpoint Tests
- All 9 search endpoints
- Authentication/authorization
- Error responses

### Performance Tests
- Batch indexing speed
- Search latency
- Memory usage

## Deployment Considerations

### Prerequisites
1. Qdrant Cloud account with active instance
2. OpenAI API key for embeddings
3. PostgreSQL database running
4. FastAPI backend running

### Environment Setup
```bash
# .env file
QDRANT_URL=https://...
QDRANT_API_KEY=...
OPENAI_API_KEY=...

# Or environment variables
export QDRANT_URL=...
export QDRANT_API_KEY=...
export OPENAI_API_KEY=...
```

### Health Checks
```bash
# Check Qdrant connection
python backend/verify_qdrant.py

# Check API endpoints
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/search/health
```

## Security Considerations

1. **API Key Protection**
   - Never commit QDRANT_API_KEY to version control
   - Use environment variables
   - Rotate keys regularly

2. **Data Privacy**
   - Organization-level filtering (automatic)
   - User authentication required for all endpoints
   - No cross-organization data leakage

3. **Vector Payload Security**
   - No sensitive data in vector metadata
   - Encrypt sensitive fields in PostgreSQL
   - Audit vector operations

## Future Enhancements

1. **Semantic Caching**
   - Cache query embeddings with Redis
   - Reduce API calls to OpenAI

2. **Hybrid Search**
   - Combine keyword search (PostgreSQL) + semantic (Qdrant)
   - Better relevance for technical queries

3. **Advanced RAG**
   - Long-context retrieval
   - Multi-stage retrieval and reranking
   - Query expansion techniques

4. **Vector Tuning**
   - Fine-tune embeddings for domain
   - Custom embedding models
   - Specialized medical/legal models

5. **Real-time Updates**
   - WebSocket support for live search results
   - Real-time document indexing
   - Streaming embeddings

## Monitoring & Observability

### Metrics to Track
- Vector search latency (p50, p95, p99)
- Embedding generation time
- Collection size growth
- Search query patterns
- Hit rates (relevant results / total searches)

### Logging
- Search queries (anonymized)
- Indexing operations
- Error events
- Performance metrics

### Alerting
- Qdrant connection failures
- Search latency > 1000ms
- Embedding API errors
- Collection size anomalies

---

**Integration Status**: ✅ Complete and Production Ready

For detailed information, see:
- `QDRANT_INTEGRATION.md` - Complete usage guide
- `QDRANT_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `verify_qdrant.py` - Verification script
