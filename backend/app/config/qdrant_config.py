"""
Qdrant Vector Database Configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional


class QdrantConfig(BaseSettings):
    """Qdrant configuration from environment variables"""
    
    # Qdrant Cloud Configuration
    qdrant_url: str = "https://d95904a7-0c84-43d2-8df3-15bfd560860a.europe-west3-0.gcp.cloud.qdrant.io:6333"
    qdrant_api_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.L5gEpZCjcAY94zC_lSlZq-1KuKGLvxXwrThrO3rNdOw"
    
    # Vector Embedding Configuration
    embedding_model: str = "text-embedding-3-small"  # OpenAI model
    embedding_dimension: int = 1536  # Dimension for text-embedding-3-small
    
    # Collection Configuration
    document_collection: str = "documents"
    conversation_collection: str = "conversations"
    
    # Search Configuration
    similarity_threshold: float = 0.7
    max_search_results: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


# Create global config instance
qdrant_config = QdrantConfig()
