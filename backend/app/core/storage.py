# backend/app/core/storage.py
"""
Storage abstraction for local dev and GCS deployment.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.observability import logs


class StorageBackend(ABC):
    """Abstract storage backend."""

    @abstractmethod
    async def upload(self, key: str, data: bytes, content_type: str = None) -> str:
        """Upload data and return the storage path/URL."""
        pass

    @abstractmethod
    async def download(self, key: str) -> bytes:
        """Download data by key."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete data by key."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass


class LocalStorage(StorageBackend):
    """Local filesystem storage for development."""

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or settings.LOCAL_STORAGE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_path(self, key: str) -> Path:
        """Get full path for a key."""
        return self.base_path / key

    async def upload(self, key: str, data: bytes, content_type: str = None) -> str:
        """Upload data to local filesystem."""
        path = self._get_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        logs.debug(f"Uploaded to local storage: {key}", "storage")
        return str(path)

    async def download(self, key: str) -> bytes:
        """Download data from local filesystem."""
        path = self._get_path(key)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {key}")
        return path.read_bytes()

    async def delete(self, key: str) -> None:
        """Delete file from local filesystem."""
        path = self._get_path(key)
        if path.exists():
            path.unlink()
            logs.debug(f"Deleted from local storage: {key}", "storage")

    async def exists(self, key: str) -> bool:
        """Check if file exists."""
        return self._get_path(key).exists()


class GCSStorage(StorageBackend):
    """Google Cloud Storage backend for production."""

    def __init__(self):
        self.bucket_name = settings.GCS_BUCKET_NAME
        self.project_id = settings.GCS_PROJECT_ID
        self._client = None

    def _get_client(self):
        """Lazy-load GCS client."""
        if self._client is None:
            try:
                from google.cloud import storage

                self._client = storage.Client(project=self.project_id)
            except ImportError:
                raise ImportError(
                    "google-cloud-storage not installed. "
                    "Install with: pip install google-cloud-storage"
                )
        return self._client

    def _get_bucket(self):
        """Get the GCS bucket."""
        return self._get_client().bucket(self.bucket_name)

    async def upload(self, key: str, data: bytes, content_type: str = None) -> str:
        """Upload data to GCS."""
        blob = self._get_bucket().blob(key)
        blob.upload_from_string(data, content_type=content_type)
        logs.debug(f"Uploaded to GCS: {key}", "storage")
        return f"gs://{self.bucket_name}/{key}"

    async def download(self, key: str) -> bytes:
        """Download data from GCS."""
        blob = self._get_bucket().blob(key)
        if not blob.exists():
            raise FileNotFoundError(f"Blob not found: {key}")
        return blob.download_as_bytes()

    async def delete(self, key: str) -> None:
        """Delete blob from GCS."""
        blob = self._get_bucket().blob(key)
        if blob.exists():
            blob.delete()
            logs.debug(f"Deleted from GCS: {key}", "storage")

    async def exists(self, key: str) -> bool:
        """Check if blob exists."""
        return self._get_bucket().blob(key).exists()


# Global storage instance
_storage: Optional[StorageBackend] = None


def get_storage() -> StorageBackend:
    """Get the configured storage backend."""
    global _storage

    if _storage is None:
        if settings.STORAGE_BACKEND == "gcs":
            _storage = GCSStorage()
            logs.info("Using GCS storage backend", "storage")
        else:
            _storage = LocalStorage()
            logs.info("Using local storage backend", "storage")

    return _storage
