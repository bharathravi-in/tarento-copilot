"""
Embedding Service
Handles vector embedding generation for documents and text
"""

import logging
from typing import List, Union
from abc import ABC, abstractmethod
import os

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""
    
    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        pass
    
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embeddings provider"""
    
    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        """Initialize OpenAI provider"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        
        if not self.api_key:
            logger.warning("OpenAI API key not found")
        
        # Try to import openai lazily
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        except ImportError:
            logger.warning("OpenAI package not installed. Embeddings will not work.")
            self.client = None
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not self.client:
            logger.error("OpenAI client not initialized")
            return []
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return []
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not self.client:
            logger.error("OpenAI client not initialized")
            return []
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            # Sort by index to maintain order
            embeddings = sorted(response.data, key=lambda x: x.index)
            return [e.embedding for e in embeddings]
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return []


class DummyEmbeddingProvider(EmbeddingProvider):
    """Dummy embedding provider for testing (generates random vectors)"""
    
    def __init__(self, dimension: int = 1536):
        """Initialize dummy provider"""
        self.dimension = dimension
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate dummy embedding"""
        import random
        return [random.uniform(-1, 1) for _ in range(self.dimension)]
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate dummy embeddings for multiple texts"""
        import random
        return [[random.uniform(-1, 1) for _ in range(self.dimension)] for _ in texts]


class EmbeddingService:
    """Service for managing embeddings"""
    
    def __init__(self, provider: EmbeddingProvider = None):
        """Initialize embedding service with provider"""
        if provider is None:
            # Default to OpenAI, fallback to dummy
            self.provider = OpenAIEmbeddingProvider()
            if not self.provider.client:
                logger.warning("Falling back to dummy embedding provider")
                self.provider = DummyEmbeddingProvider()
        else:
            self.provider = provider
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return []
        
        return await self.provider.generate_embedding(text)
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not texts:
            logger.warning("Empty texts list provided for embedding")
            return []
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            return []
        
        return await self.provider.generate_embeddings(valid_texts)
    
    async def embed_document(self, title: str, content: str, metadata: str = "") -> List[float]:
        """
        Generate embedding for a document
        Combines title, content, and metadata for better representation
        """
        # Create a meaningful text representation
        text_parts = [title]
        if content:
            text_parts.append(content[:1000])  # Limit content to first 1000 chars
        if metadata:
            text_parts.append(metadata)
        
        combined_text = " ".join(text_parts)
        return await self.embed_text(combined_text)


# Create global embedding service
embedding_service = EmbeddingService()
