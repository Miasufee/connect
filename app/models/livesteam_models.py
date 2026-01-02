from datetime import datetime, timezone
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.models import TimestampMixin, VisibilityStatus, StreamType, ParticipantRole, TitleMixin, \
    DescriptionMixin, ZawiyaIdMixin, UserIdMixin, GroupIdMixin
from .enums import StreamStatus, RecordingStatus, LiveStreamEventType


class LiveStream(Document, TimestampMixin, ZawiyaIdMixin, TitleMixin, DescriptionMixin, UserIdMixin, GroupIdMixin):
    streamer_id: PydanticObjectId  # creator / owner

    status: StreamStatus = StreamStatus.CREATED
    is_recorded: bool = True
    visibility: VisibilityStatus = VisibilityStatus.PUBLIC
    stream_type: StreamType = StreamType.ONE_TO_MANY

    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    class Settings:
        name = "live_streams"
        indexes = [
            "zawiya_id",
            "status",
            "visibility",
        ]


class StreamAnalytics(Document, TimestampMixin):
    stream_id: PydanticObjectId

    likes: int = Field(default=0, ge=0)
    viewers: int = Field(default=0, ge=0)

    class Settings:
        name = "stream_analytics"
        indexes = [
            "stream_id",
        ]

class LiveStreamParticipant(Document, TimestampMixin):
    stream_id: PydanticObjectId
    user_id: PydanticObjectId
    role: ParticipantRole = ParticipantRole.VIEWER

    # Permission flags
    can_publish_audio: bool = False
    can_publish_video: bool = False
    can_share_screen: bool = False
    is_muted: bool = False
    is_banned: bool = False

    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    left_at: Optional[datetime] = None

    class Settings:
        name = "live_stream_participants"
        indexes = [
            [("stream_id", 1), ("user_id", 1)],
            "stream_id",
        ]
class Recording(Document, TimestampMixin):
    stream_id: PydanticObjectId

    storage_path: str  # S3 / GCS / local path
    format: str = "mp4"

    duration_seconds: Optional[int] = None
    size_bytes: Optional[int] = None
    status: RecordingStatus = RecordingStatus.PENDING

    class Settings:
        name = "recordings"
        indexes = ["stream_id"]



class LiveStreamEvent(Document, TimestampMixin):
    stream_id: PydanticObjectId
    actor_id: PydanticObjectId
    target_id: Optional[PydanticObjectId] = None

    event_type: LiveStreamEventType
    reason: Optional[str] = None

    class Settings:
        name = "live_stream_events"
        indexes = ["stream_id", "actor_id", "target_id"]