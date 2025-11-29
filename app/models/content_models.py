from datetime import datetime
from enum import Enum
from typing import Optional
from beanie import Document, PydanticObjectId

from app.models.models_base import (
    TimestampMixin, SoftDeleteMixin, TitleMixin, DescriptionMixin,
    UserIdMixin, ZawiyaIdMixin, utc_now
)


class VideoStatus(Enum):
    Uploading = "Uploading"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"


class LiveStreamStatus(Enum):
    Waiting = "Waiting"
    Live = "Live"
    Ended = "Ended"
    Cancelled = "Cancelled"
    Error = "Error"


class Video(
    Document,
    TimestampMixin,
    SoftDeleteMixin,
    TitleMixin,
    DescriptionMixin,
    UserIdMixin,
    ZawiyaIdMixin,
):
    """Video metadata"""

    video_url: str
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None
    size_in_mb: Optional[float] = None
    format: Optional[str] = None
    video_status: VideoStatus = VideoStatus.Uploading
    is_publish: bool = False

    class Settings:
        name = "videos"
        indexes = [
            "zawiya_id"
        ]


class VideoAnalytics(Document, TimestampMixin):
    """Video analytics"""

    video_id: PydanticObjectId
    total_views: int = 0
    total_likes: int = 0
    total_dislikes: int = 0
    average_watch_time: Optional[float] = 0.0

    class Settings:
        name = "video_analytics"


class LiveStream(
    Document,
    TimestampMixin,
    SoftDeleteMixin,
    TitleMixin,
    DescriptionMixin,
    UserIdMixin,
    ZawiyaIdMixin,
):
    stream_key: str
    status: LiveStreamStatus = LiveStreamStatus.Waiting
    start_time: datetime = utc_now()
    end_time: Optional[datetime] = None
    record_to_video: bool = True
    playback_url: Optional[str] = None

    class Settings:
        name = "livestreams"


class LivestreamAnalytics(Document, TimestampMixin):
    livestream_id: PydanticObjectId
    livestream_likes: int = 0
    total_viewers: int = 0
    peak_viewers: int = 0
    total_watch_time: float = 0.0

    class Settings:
        name = "livestream_analytics"

class Image(
    Document,
    TimestampMixin,
    SoftDeleteMixin,
    TitleMixin,
    DescriptionMixin,
    UserIdMixin,
    ZawiyaIdMixin
):
    pass