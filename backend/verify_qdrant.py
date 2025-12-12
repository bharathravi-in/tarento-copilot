"""
Qdrant Connection Verification Script
Tests connection and basic operations
"""

import asyncio
import sys
from app.config.qdrant_config import qdrant_config
from app.services.qdrant_service import qdrant_service
from app.services.embedding_service import embedding_service


async def verify_qdrant_connection():
    """Verify Qdrant connection and configuration"""
    
    print("=" * 60)
    print("Qdrant Vector Database Verification")
    print("=" * 60)
    
    # 1. Configuration Check
    print("\n1. Configuration Check:")
    print(f"   - URL: {qdrant_config.qdrant_url[:50]}...")
    print(f"   - API Key: {qdrant_config.qdrant_api_key[:20]}...")
    print(f"   - Embedding Model: {qdrant_config.embedding_model}")
    print(f"   - Embedding Dimension: {qdrant_config.embedding_dimension}")
    print(f"   - Collections:")
    print(f"     * Document Collection: {qdrant_config.document_collection}")
    print(f"     * Conversation Collection: {qdrant_config.conversation_collection}")
    
    # 2. Health Check
    print("\n2. Health Status Check:")
    try:
        health = qdrant_service.get_health_status()
        print(f"   - Status: {health['status']}")
        print(f"   - Collections: {health['collections']}")
        if 'models' in health:
            print(f"   - Available Collections: {', '.join(health['models'])}")
    except Exception as e:
        print(f"   - Error: {str(e)}")
        return False
    
    # 3. Collection Management
    print("\n3. Collection Management:")
    try:
        collections = qdrant_service.list_collections()
        print(f"   - Found {len(collections)} collections:")
        for col in collections:
            print(f"     * {col}")
            info = qdrant_service.get_collection_info(col)
            if info:
                print(f"       - Points: {info.get('points_count', 'N/A')}")
                print(f"       - Size: {info.get('disk_data_size', 'N/A')} bytes")
    except Exception as e:
        print(f"   - Error: {str(e)}")
    
    # 4. Embedding Test
    print("\n4. Embedding Generation Test:")
    try:
        test_text = "This is a test document for embedding"
        embedding = await embedding_service.embed_text(test_text)
        print(f"   - Text: '{test_text}'")
        print(f"   - Embedding Dimension: {len(embedding)}")
        print(f"   - Sample Values: {embedding[:5]}")
    except Exception as e:
        print(f"   - Error: {str(e)}")
        return False
    
    # 5. Vector Operation Test
    print("\n5. Vector Operation Test:")
    try:
        # Create test collection
        test_collection = "test_collection"
        created = qdrant_service.create_collection(test_collection, 1536)
        print(f"   - Created test collection: {created}")
        
        # Add test vector
        test_vector = [0.1] * 1536
        added = qdrant_service.add_document_vector(
            collection_name=test_collection,
            document_id="test_doc_1",
            vector=test_vector,
            metadata={"title": "Test Document"},
            organization_id="test_org"
        )
        print(f"   - Added test vector: {added}")
        
        # Search test
        query_vector = [0.1] * 1536
        results = qdrant_service.search_similar(
            collection_name=test_collection,
            query_vector=query_vector,
            organization_id="test_org",
            limit=5
        )
        print(f"   - Search returned {len(results)} results")
        if results:
            print(f"   - Top result score: {results[0]['score']:.4f}")
        
        # Cleanup
        deleted = qdrant_service.delete_collection(test_collection)
        print(f"   - Cleaned up test collection: {deleted}")
        
    except Exception as e:
        print(f"   - Error: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Verification Complete!")
    print("=" * 60)
    return True


async def main():
    """Run verification"""
    try:
        success = await verify_qdrant_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Verification Failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
