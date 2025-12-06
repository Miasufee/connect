from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Any

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.models import VisibilityStatus, StreamStatus, RecordingStatus
from app.models.models_base import SoftDeleteMixin, TimestampMixin

class StreamBase(Document, TimestampMixin, SoftDeleteMixin):
    """
    Reusable base class for livestream models
    """

    # TTL expiration
    ttl_at: Optional[datetime] = None  # mongo TTL index in Settings

    # version control
    version: int = 1

    # audit logs
    created_by: Optional[PydanticObjectId] = None
    updated_by: Optional[PydanticObjectId] = None

    # RBAC
    allowed_roles: Optional[List[str]] = None
    required_scopes: Optional[List[str]] = None

    # free metadata
    tags: Optional[List[str]] = None
    metadata: Optional[dict[str, Any]] = None

    async def soft_save(self):
        self.version += 1
        await self.save()

    class Settings:
        validate_on_save = True
        use_revision = True

class Stream(StreamBase):
    owner_id: PydanticObjectId
    zawiya_id: PydanticObjectId

    title: str = Field(..., min_length=3)
    description: Optional[str] = None

    stream_key: str
    status: StreamStatus = StreamStatus.CREATED
    visibility: VisibilityStatus = VisibilityStatus.PRIVATE

    ingest_url: Optional[str] = None
    playback_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None

    viewer_count: int = 0
    max_viewers: int = 0

    class Settings:
        name = "streams"
        indexes = [
            "owner_id",
            {"keys": [("stream_key", 1)], "unique": True},
            [("title", "text"), ("description", "text")],   # text search
            {"keys": [("ttl_at", 1)], "expireAfterSeconds": 0},  # TTL
        ]

class Recording(StreamBase):
    stream_id: PydanticObjectId

    status: RecordingStatus = RecordingStatus.PENDING
    duration_seconds: Optional[int] = None

    storage_path: Optional[str] = None
    manifest_path: Optional[str] = None

    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None

    error_message: Optional[str] = None

    node_id: Optional[str] = None
    segment_prefix: Optional[str] = None

    class Settings:
        name = "recordings"
        indexes = [
            "stream_id",
            "status",
            "node_id",
            {"keys": [("ttl_at", 1)], "expireAfterSeconds": 0},
        ]

class Rendition(StreamBase):
    recording_id: PydanticObjectId

    quality: str
    resolution: str
    bitrate_kbps: int
    codec: str
    storage_path: str
    file_size_bytes: Optional[int] = None

    class Settings:
        name = "renditions"
        indexes = [
            "recording_id",
            "quality",
        ]

class HLSSegment(StreamBase):
    recording_id: PydanticObjectId

    sequence: int
    duration: float
    storage_path: str
    byte_size: Optional[int] = None

    class Settings:
        name = "hls_segments"
        indexes = [
            "recording_id",
            "sequence",
        ]
class StreamEvent(StreamBase):
    stream_id: PydanticObjectId

    event_type: str
    event_data: Optional[dict[str, Any]] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

    class Settings:
        name = "stream_events"
        indexes = [
            "stream_id",
            "event_type",
            "created_at",
        ]

class Subtitle(StreamBase):
    recording_id: PydanticObjectId

    language: str
    format: str = "vtt"
    storage_path: str
    is_auto_generated: bool = True

    class Settings:
        name = "subtitles"
        indexes = [
            "recording_id",
            "language",
        ]
