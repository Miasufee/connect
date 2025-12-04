from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from beanie import Document, PydanticObjectId, before_event, Insert, Replace, SaveChanges
from pydantic import BaseModel, Field


# -----------------------------
# Models
# -----------------------------

class Video(Document, TimestampMixin, SoftDeleteMixin, TitleMixin, DescriptionMixin, UserIdMixin, ZawiyaIdMixin):
    """Main video catalog document."""

    video_url: str
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    size_in_bytes: Optional[int] = None
    format: Optional[str] = None
    video_status: VideoStatus = Field(default=VideoStatus.UPLOADING)
    is_published: bool = Field(default=False)

    class Settings:
        name = "videos"
        indexes = ["zawiya_id", "user_id", "video_status"]


class VideoAnalytics(Document, TimestampMixin):
    """Aggregated analytics for a video. Keep small and frequently-updated counters.
    """

    video_id: PydanticObjectId
    total_views: int = 0
    total_likes: int = 0
    total_dislikes: int = 0
    average_watch_time_seconds: float = 0.0

    class Settings:
        name = "video_analytics"
        indexes = ["video_id"]


class Stream(Document, TimestampMixin, SoftDeleteMixin, TitleMixin, DescriptionMixin, UserIdMixin, ZawiyaIdMixin):
    """Represents a stream session and metadata used for ingest/playback.

    - owner/user fields are explicit for permission checks and indexing.
    - status should be toggled by your streaming control plane.
    """

    # identifiers
    stream_key: str

    # status & visibility
    status: StreamStatus = Field(default=StreamStatus.CREATED)
    visibility: str = Field(default="private")

    # urls
    ingest_url: Optional[str] = None
    playback_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    # timing
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None

    # viewers
    viewer_count: int = 0
    max_viewers: int = 0

    # free-form metadata
    metadata: Optional[Dict[str, Any]] = None

    class Settings:
        name = "streams"
        indexes = ["owner_id", "zawiya_id", "stream_key", "status"]


class Recording(Document, TimestampMixin):
    """Recording pieces for a stream. Use one doc per completed recording manifest.
    For fragmented/segment-level data, keep separate collection or storage bucket.
    """

    stream_id: PydanticObjectId
    status: RecordingStatus = Field(default=RecordingStatus.PENDING)

    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None

    # Storage paths (object storage recommended)
    storage_path: Optional[str] = None
    manifest_path: Optional[str] = None

    # processing lifecycle
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Settings:
        name = "recordings"
        indexes = ["stream_id", "status"]


class Rendition(Document, TimestampMixin):
    recording_id: PydanticObjectId

    quality_label: str  # e.g. "1080p"
    resolution: str  # e.g. "1920x1080"
    bitrate_kbps: int
    codec: Optional[str] = None

    storage_path: str
    file_size_bytes: Optional[int] = None

    class Settings:
        name = "renditions"
        indexes = ["recording_id"]


class Thumbnail(Document, TimestampMixin, SoftDeleteMixin):
    stream_id: PydanticObjectId

    timestamp_seconds: float
    storage_path: str
    width: int
    height: int
    is_primary: bool = False

    class Settings:
        name = "thumbnails"
        indexes = ["stream_id", "is_primary"]


class Subtitle(Document, TimestampMixin, SoftDeleteMixin):
    recording_id: PydanticObjectId

    language: str
    format: str = Field(default="vtt")
    storage_path: str
    is_auto_generated: bool = Field(default=True)

    class Settings:
        name = "subtitles"
        indexes = ["recording_id", "language"]


class StreamEvent(Document, TimestampMixin):
    stream_id: PydanticObjectId
    event_type: StreamEventType
    event_data: Optional[Dict[str, Any]] = None

    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

    class Settings:
        name = "stream_events"
        indexes = ["stream_id", "event_type"]
