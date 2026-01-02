from typing import List
from beanie import Document, PydanticObjectId
from app.models import TimestampMixin, ZawiyaIdMixin, GroupIdMixin, UserIdMixin, TitleMixin, DescriptionMixin


class Image(Document, TimestampMixin):
    file_path: str
    width: int
    height: int
    size_bytes: int

    class Settings:
        name = "images"

class ImageGallery(Document, TimestampMixin, ZawiyaIdMixin, GroupIdMixin, UserIdMixin, TitleMixin, DescriptionMixin):
    image_ids: List[PydanticObjectId]  # references Image
    caption: str | None = None

    class Settings:
        name = "image_galleries"
