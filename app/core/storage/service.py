from .base import StorageBackend


class StorageService:
    def __init__(self, backend: StorageBackend):
        self.backend = backend

    async def upload(self, *args, **kwargs):
        return await self.backend.upload(*args, **kwargs)

    async def download(self, key: str) -> bytes:
        return await self.backend.download(key)

    async def delete(self, key: str) -> None:
        return await self.backend.delete(key)

    async def exists(self, key: str) -> bool:
        return await self.backend.exists(key)

    async def url(self, key: str, expires: int | None = None) -> str:
        return await self.backend.get_url(key, expires)
