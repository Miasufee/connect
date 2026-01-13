from app.core.processing.thumbnail_async import AsyncThumbnailService
from app.core.storage.base import StorageBackend
from app.crud.content.image_crud import image_crud


class ImageService:
    def __init__(self, storage: StorageBackend):
        self.storage = storage

    async def upload_image_with_thumbnail(
        self,
        image_bytes: bytes,
        key: str,
        user_id,
    ):
        # 1. Upload original
        original_path = await self.storage.upload(
            image_bytes, key, content_type="image/jpeg"
        )

        # 2. Generate thumbnail
        thumb_bytes = await AsyncThumbnailService.generate(
            image_bytes, width=300
        )

        thumb_path = await self.storage.upload(
            thumb_bytes, f"thumbs/{key}", content_type="image/jpeg"
        )

        # 3. Save metadata
        return await image_crud.create(
            file_path=original_path,
            thumbnail_path=thumb_path,
            size_bytes=len(image_bytes),
            user_id=user_id,
        )
