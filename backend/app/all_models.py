# backend/app/all_models.py
"""Centralized model imports for Alembic migrations."""

from app.core.database import Base
from app.features.rag.models import Document, DocumentChunk

# Export metadata for Alembic
metadata = Base.metadata

__all__ = ["Document", "DocumentChunk", "metadata", "Base"]
