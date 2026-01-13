from abc import ABC, abstractmethod
from typing import Optional


class StorageBackend(ABC):
    """
    Contract for any storage backend (local, S3, MinIO, etc.)
    """

    @abstractmethod
    async def upload(
        self,
        data: bytes,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """Store data and return storage path"""
        raise NotImplementedError

    @abstractmethod
    async def download(self, key: str) -> bytes:
        """Download file as bytes"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete file"""
        raise NotImplementedError

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if file exists"""
        raise NotImplementedError

    @abstractmethod
    async def get_url(self, key: str, expires: Optional[int] = None) -> str:
        """Return public or signed URL"""
        raise NotImplementedError
