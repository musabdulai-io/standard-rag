# backend/app/core/config.py
"""
Application configuration using Pydantic Settings.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_NAME: str = "standard-rag"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # API
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/standard_rag"

    # Pinecone
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX: str = "standard-rag"
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSION: int = 1024
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = 1024
    OPENAI_TEMPERATURE: float = 0.3

    # RAG Settings
    CHUNK_MIN_SIZE: int = 800
    CHUNK_MAX_SIZE: int = 2000
    CHUNK_OVERLAP: int = 200
    SEARCH_TOP_K: int = 10
    SEARCH_SCORE_THRESHOLD: float = 0.5

    # Security
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    MAX_INPUT_LENGTH: int = 10000
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Storage (local dev vs GCS deployment)
    STORAGE_BACKEND: str = "local"  # "local" or "gcs"
    LOCAL_STORAGE_PATH: str = "./storage"
    GCS_BUCKET_NAME: Optional[str] = None
    GCS_PROJECT_ID: Optional[str] = None

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
