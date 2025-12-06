from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Any

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.models import VideoStatus, VideoVisibility
from app.models.models_base import SoftDeleteMixin, TimestampMixin


class VideoBase(Document, TimestampMixin, SoftDeleteMixin):
    """
    Shared metadata for all video-type entities in your platform.
    """

    # RBAC / Auth
    allowed_roles: Optional[List[str]] = None
    required_scopes: Optional[List[str]] = None

    # metadata
    tags: Optional[List[str]] = None
    metadata: Optional[dict[str, Any]] = None

    # audit logs
    created_by: Optional[PydanticObjectId] = None
    updated_by: Optional[PydanticObjectId] = None

    # event version (important for processing)
    version: int = 1

    # TTL automatic removal
    ttl_at: Optional[datetime] = None

    async def soft_save(self):
        self.version += 1
        await self.save()

    class Settings:
        validate_on_save = True
        use_revision = True     # event history enabled

class Video(VideoBase):
    owner_id: PydanticObjectId
    zawiya_id: PydanticObjectId

    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None

    original_file_path: Optional[str] = None
    thumbnail_url: Optional[str] = None
    playback_url: Optional[str] = None

    status: VideoStatus = VideoStatus.UPLOADED
    visibility: VideoVisibility = VideoVisibility.PRIVATE

    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None

    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[int] = None

    views_count: int = 0
    likes_count: int = 0
    dislikes_count: int = 0

    # playlist or categories
    category: Optional[str] = None

    class Settings:
        name = "videos"
        indexes = [
            "owner_id",
            "status",
            "visibility",
            ("title", "text"),
            ("description", "text"),
            {"keys": [("ttl_at", 1)], "expireAfterSeconds": 0},
        ]

class VideoRendition(VideoBase):
    video_id: PydanticObjectId

    quality: str           # 1080p, 720p, etc.
    resolution: str        # 1920x1080
    bitrate_kbps: int
    codec: str
    storage_path: str

    file_size_bytes: Optional[int] = None

    class Settings:
        name = "video_renditions"
        indexes = [
            "video_id",
            "quality",
        ]

class VideoHLSSegment(VideoBase):
    video_id: PydanticObjectId

    sequence: int
    duration: float
    storage_path: str
    byte_size: Optional[int] = None

    # distributed recording node / region
    node_id: Optional[str] = None

    class Settings:
        name = "video_hls_segments"
        indexes = [
            "video_id",
            "sequence",
            "node_id",
        ]

class VideoEvent(VideoBase):
    video_id: PydanticObjectId

    event_type: str
    event_data: Optional[dict[str, Any]] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

    class Settings:
        name = "video_events"
        indexes = [
            "video_id",
            "event_type",
            "created_at",
        ]

class VideoSubtitle(VideoBase):
    video_id: PydanticObjectId

    language: str
    format: str = "vtt"
    storage_path: str

    is_auto_generated: bool = True

    class Settings:
        name = "video_subtitles"
        indexes = [
            "video_id",
            "language",
        ]
