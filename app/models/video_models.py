from beanie import Document

from app.models import TimestampMixin, VideoStatus, TitleMixin, DescriptionMixin, ZawiyaIdMixin, UserIdMixin, \
    GroupIdMixin


class Video(Document, TimestampMixin, TitleMixin, DescriptionMixin, ZawiyaIdMixin, UserIdMixin, GroupIdMixin):
    file_path: str
    status: VideoStatus = VideoStatus.UPLOADED

    class Settings:
        name = "videos"
        indexes = ["content_id"]
