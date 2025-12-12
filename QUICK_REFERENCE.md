# Quick Reference: Qdrant Setup & Testing

## Status Check

### Is Qdrant Connected?
```bash
cd backend && python3 -c "
from app.services.qdrant_service import qdrant_service
print(qdrant_service.get_health_status())
"
```

**Expected:**
```
{'status': 'healthy', 'collections': 1, 'models': ['documents']}
```

### How Many Documents Are Indexed?
```bash
cd backend && python3 -c "
from app.services.qdrant_service import qdrant_service
info = qdrant_service.get_collection_info('documents')
print(f'Documents in Qdrant: {info[\"points_count\"]}')
"
```

### Are Documents Marked as Indexed?
```bash
cd backend && python3 << 'EOF'
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://tarento:tarento_dev@localhost:5432/tarento_db")
with engine.connect() as conn:
    docs = conn.execute(text("SELECT title, is_indexed FROM documents")).fetchall()
    for title, is_indexed in docs:
        print(f"{'✅' if is_indexed else '❌'} {title}")
EOF
```

---

## Reindex Documents

### Reindex Everything
```bash
cd backend && python3 reindex_documents.py
```

### Reindex Manually (Step by Step)
```bash
cd backend && python3 << 'EOF'
import asyncio
from app.services.qdrant_service import qdrant_service
from app.api.v1.documents import index_document_vector
from sqlalchemy import create_engine, text

async def reindex_one():
    # Get one document
    engine = create_engine("postgresql://tarento:tarento_dev@localhost:5432/tarento_db")
    with engine.connect() as conn:
        doc = conn.execute(text("""
            SELECT id, title, content, description, organization_id 
            FROM documents LIMIT 1
        """)).first()
        
        if doc:
            print(f"Indexing: {doc[1]}")
            await index_document_vector(
                document_id=doc[0],
                title=doc[1],
                content=doc[2],
                organization_id=str(doc[4]),
                description=doc[3]
            )
            print("✅ Done!")

asyncio.run(reindex_one())
EOF
```

---

## Enable OpenAI (Real Embeddings)

### Step 1: Get API Key
- Go to https://platform.openai.com/api-keys
- Create new API key
- Copy the key (starts with `sk-`)

### Step 2: Add to .env
```bash
# backend/.env
OPENAI_API_KEY="sk-your-key-here"
```

### Step 3: Restart Backend
```bash
pkill -f uvicorn
cd backend && uvicorn app.main:app --reload
```

### Step 4: Reindex Documents
```bash
cd backend && python3 reindex_documents.py
```

### Verify Real Embeddings
```bash
cd backend && python3 -c "
from app.services.embedding_service import embedding_service
print(f'Provider: {embedding_service.provider.__class__.__name__}')
"
```

**Expected:**
```
Provider: OpenAIEmbeddingProvider
```

---

## Troubleshooting

### Documents Not Indexing
1. Check Qdrant connection: `qdrant_service.get_health_status()`
2. Check collection exists: `qdrant_service.list_collections()`
3. Check backend logs: `tail -50 /tmp/backend.log`
4. Reindex manually: `python3 reindex_documents.py`

### Reindex Failing
```bash
# Full debug reindex
cd backend && python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
exec(open('reindex_documents.py').read())
"
```

### Backend Won't Start
```bash
# Check logs
tail -100 /tmp/backend.log | tail -30

# Check Python syntax
python3 -m py_compile app/main.py app/services/qdrant_service.py

# Restart cleanly
pkill -9 -f uvicorn
sleep 2
cd backend && uvicorn app.main:app --reload
```

---

## Files Changed

| File | Change |
|------|--------|
| `backend/app/main.py` | Added startup event |
| `backend/app/services/qdrant_service.py` | Removed invalid config, fixed attributes |
| `backend/reindex_documents.py` | NEW - reindex utility |

---

## Test Document Creation & Indexing

### Via UI
```
1. Go to http://localhost:5173/documents
2. Click "Create Document"
3. Fill in title and content
4. Click "Create"
5. Document should appear in list
```

### Via API
```bash
curl -X POST http://localhost:8000/api/v1/documents/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Document",
    "content": "This is a test",
    "is_public": true
  }'
```

### Verify Indexing
```bash
# Wait 2 seconds for async indexing
sleep 2

# Check Qdrant
python3 -c "
from app.services.qdrant_service import qdrant_service
info = qdrant_service.get_collection_info('documents')
print(f'Points: {info[\"points_count\"]}')
"
```

---

## System Requirements Check

```bash
# Qdrant Connected?
python3 -c "
from app.services.qdrant_service import qdrant_service
print('Qdrant:', qdrant_service.get_health_status()['status'])
"

# PostgreSQL Connected?
python3 << 'EOF'
from sqlalchemy import create_engine
engine = create_engine("postgresql://tarento:tarento_dev@localhost:5432/tarento_db")
with engine.connect() as conn:
    print("PostgreSQL: OK")
EOF

# Embeddings Working?
python3 -c "
import asyncio
from app.services.embedding_service import embedding_service
emb = asyncio.run(embedding_service.embed_text('test'))
print(f'Embeddings: OK (dim={len(emb)})')
"
```

**Expected Output:**
```
Qdrant: healthy
PostgreSQL: OK
Embeddings: OK (dim=1536)
```

---

## Performance Notes

- Indexing is async (happens in background)
- Wait ~1-2 seconds after document creation for indexing
- Reindexing all documents takes ~10-30 seconds
- Dummy embeddings: ~100ms per document
- Real embeddings (OpenAI): ~200-500ms per document

---

## Next Steps

### Immediate
- ✅ Documents now indexed in Qdrant
- ✅ System ready for use
- ✅ Backend logs show what's happening

### Optional
- Add OpenAI API key for real embeddings
- Test semantic search (Phase 3.3)
- Set up monitoring/alerting
- Document API endpoints

---

## Support

**Issue:** Documents not showing in Qdrant  
**Solution:** Run `python3 reindex_documents.py`

**Issue:** "No module named openai"  
**Solution:** Edit `.env`, remove OPENAI_API_KEY line, or install: `pip install openai`

**Issue:** Qdrant connection refused  
**Solution:** Check Qdrant URL in `.env`, ensure network connectivity

**Issue:** Dummy embeddings used  
**Solution:** Add OPENAI_API_KEY to `.env` and restart backend

---

**Last Updated:** December 12, 2025  
**Status:** ✅ WORKING
