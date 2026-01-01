from datetime import datetime
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.models import TimestampMixin, VisibilityStatus, StreamType, ParticipantRole, SFUType
from .enums import StreamStatus, RecordingStatus, LiveStreamEventType, VideoStatus


class LiveStream(Document, TimestampMixin):
    zawiya_id: PydanticObjectId
    streamer_id: PydanticObjectId  # creator / owner
    content_id: PydanticObjectId
    group_id: Optional[PydanticObjectId] = None

    title: str = Field(min_length=5, max_length=500)
    description: Optional[str] = None

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

    joined_at: datetime = Field(default_factory=datetime.utcnow)
    left_at: Optional[datetime] = None

    class Settings:
        name = "live_stream_participants"
        indexes = [
            [("stream_id", 1), ("user_id", 1)],
            "stream_id",
        ]

class WebRTCSession(Document, TimestampMixin):
    stream_id: PydanticObjectId
    sfu_type: SFUType = SFUType.MEDIA_SOUP  # media-soup / livekit / janus / custom
    sfu_room_id: str  # SFU room identifier
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    class Settings:
        name = "webrtc_sessions"
        indexes = ["stream_id", "sfu_room_id"]


class WebRTCPeer(Document, TimestampMixin):
    session_id: PydanticObjectId
    user_id: PydanticObjectId

    peer_id: str  # internal SFU peer ID
    is_publishing_audio: bool = False
    is_publishing_video: bool = False
    is_screen_sharing: bool = False

    connected_at: datetime = Field(default_factory=datetime.utcnow)
    disconnected_at: Optional[datetime] = None

    class Settings:
        name = "webrtc_peers"
        indexes = [
            [("session_id", 1)],
            [("user_id", 1)],
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