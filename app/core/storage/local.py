import aiofiles
from pathlib import Path

from .base import StorageBackend


class LocalStorage(StorageBackend):
    def __init__(self, base_path: str = "media"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _full_path(self, key: str) -> Path:
        return self.base_path / key

    async def upload(
        self,
        data: bytes,
        key: str,
        content_type: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        path = self._full_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(path, "wb") as f:
            await f.write(data)

        return str(path)

    async def download(self, key: str) -> bytes:
        path = self._full_path(key)
        async with aiofiles.open(path, "rb") as f:
            return await f.read()

    async def delete(self, key: str) -> None:
        path = self._full_path(key)
        if path.exists():
            path.unlink()

    async def exists(self, key: str) -> bool:
        return self._full_path(key).exists()

    async def get_url(self, key: str, expires: int | None = None) -> str:
        # Local files are accessed via static serving
        return f"/media/{key}"
