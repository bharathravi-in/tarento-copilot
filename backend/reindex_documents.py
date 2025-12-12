#!/usr/bin/env python3
"""
Reindex All Documents in Qdrant
==============================

This script reindexes all documents from PostgreSQL to Qdrant.
Use this after:
  1. Configuring OpenAI API key
  2. Setting up Qdrant collection
  3. When you want to re-embed documents with new embeddings

Usage:
    python3 reindex_documents.py
"""

import asyncio
import os
import sys
import logging
from sqlalchemy import create_engine, text
from datetime import datetime

# Setup environment
os.environ.setdefault('ENVIRONMENT', 'development')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from app.services.qdrant_service import qdrant_service
from app.services.embedding_service import embedding_service
from app.api.v1.documents import index_document_vector


async def reindex_all_documents():
    """Reindex all documents with content"""
    
    # Database connection
    db_url = "postgresql://tarento:tarento_dev@localhost:5432/tarento_db"
    engine = create_engine(db_url)
    
    print("\n" + "="*70)
    print("DOCUMENT REINDEXING UTILITY")
    print("="*70)
    
    # Step 1: Verify Qdrant connection
    print("\n[1] Verifying Qdrant Connection...")
    try:
        status = qdrant_service.get_health_status()
        if status['status'] == 'healthy':
            print("    ✅ Qdrant: HEALTHY")
        else:
            print(f"    ❌ Qdrant: {status['status']}")
            print(f"       Error: {status.get('error', 'Unknown error')}")
            return
    except Exception as e:
        print(f"    ❌ Failed to connect to Qdrant: {e}")
        return
    
    # Step 2: Check embedding provider
    print("\n[2] Checking Embedding Provider...")
    provider_name = embedding_service.provider.__class__.__name__
    print(f"    Provider: {provider_name}")
    if provider_name == "DummyEmbeddingProvider":
        print("    ⚠️  WARNING: Using dummy embeddings (random vectors)")
        print("       To use real semantic embeddings, configure OPENAI_API_KEY in .env")
    
    # Step 3: Fetch documents
    print("\n[3] Fetching documents from PostgreSQL...")
    with engine.connect() as conn:
        docs = conn.execute(text("""
            SELECT id, title, content, description, organization_id 
            FROM documents 
            WHERE content IS NOT NULL AND content != ''
            ORDER BY created_at DESC
        """)).fetchall()
        
        if not docs:
            print("    ⚠️  No documents with content found")
            return
        
        print(f"    ✅ Found {len(docs)} documents to reindex")
    
    # Step 4: Reindex documents
    print("\n[4] Reindexing documents...")
    print("-" * 70)
    
    success_count = 0
    error_count = 0
    
    for i, (doc_id, title, content, desc, org_id) in enumerate(docs, 1):
        try:
            # Show progress
            title_display = title[:50] if title else "Untitled"
            print(f"    [{i:2d}/{len(docs)}] {title_display}...", end=" ")
            
            # Index document
            await index_document_vector(
                document_id=doc_id,
                title=title or "Untitled",
                content=content or "",
                organization_id=str(org_id),
                description=desc
            )
            
            print("✅")
            success_count += 1
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)[:40]}")
            error_count += 1
    
    # Step 5: Update database flags
    print("\n[5] Updating document index flags...")
    try:
        with engine.begin() as conn:
            result = conn.execute(text("""
                UPDATE documents 
                SET is_indexed = TRUE, updated_at = NOW()
                WHERE content IS NOT NULL AND content != ''
            """))
            updated = result.rowcount
            print(f"    ✅ Updated {updated} documents")
    except Exception as e:
        print(f"    ❌ Error updating flags: {e}")
    
    # Step 6: Verify results
    print("\n[6] Verifying Qdrant collection...")
    try:
        info = qdrant_service.get_collection_info("documents")
        if info:
            print(f"    ✅ Collection: documents")
            print(f"       Points: {info.get('points_count', 0)}")
            print(f"       Vectors: {info.get('vectors_count', 0)}")
        else:
            print("    ⚠️  Could not get collection info")
    except Exception as e:
        print(f"    ⚠️  Error: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("REINDEXING SUMMARY")
    print("="*70)
    print(f"Total Documents:  {len(docs)}")
    print(f"Successful:       {success_count} ✅")
    print(f"Failed:           {error_count} ❌")
    print(f"Success Rate:     {(success_count/len(docs)*100):.1f}%")
    
    if error_count == 0:
        print("\n✅ All documents reindexed successfully!")
    else:
        print(f"\n⚠️  {error_count} documents failed to reindex")
        print("   Check the errors above and retry if needed")
    
    print("="*70 + "\n")


async def main():
    """Main entry point"""
    try:
        await reindex_all_documents()
    except KeyboardInterrupt:
        print("\n\n⚠️  Reindexing cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
