from typing import Optional
from beanie import Document, PydanticObjectId
from app.models import TimestampMixin, AudioStatus, ZawiyaIdMixin, GroupIdMixin, UserIdMixin, TitleMixin, \
    DescriptionMixin


class Audio(Document, TimestampMixin, ZawiyaIdMixin, GroupIdMixin, UserIdMixin, TitleMixin, DescriptionMixin):
    file_path: str
    duration_seconds: int
    size_bytes: int

    status: AudioStatus = AudioStatus.PROCESSING

    class Settings:
        name = "audios"
