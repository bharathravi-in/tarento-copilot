"""
Configuration management for Tarento Application
Supports multiple environments: development, testing, production
"""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with support for environment variables"""
    
    # Application
    app_name: str = "Tarento Enterprise AI Co-Pilot"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql://tarento:tarento_dev@localhost:5432/tarento_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "tarento_documents"
    
    # JWT
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # API
    api_v1_str: str = "/api/v1"
    
    # CORS
    allowed_origins: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Google Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-pro"
    
    # Google Agent Development Kit
    google_adk_enabled: bool = True
    google_adk_cache_threshold: int = 100
    google_adk_max_tokens: int = 4096
    google_adk_temperature: float = 0.7
    
    # Google Cloud
    google_cloud_project: str = ""
    google_cloud_location: str = "us-central1"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


settings = Settings()
