from beanie import Document, PydanticObjectId

from app.models import TimestampMixin, VideoStatus


class Video(Document, TimestampMixin):
    content_id: PydanticObjectId
    file_path: str
    status: VideoStatus

    class Settings:
        name = "videos"
        indexes = ["content_id"]
