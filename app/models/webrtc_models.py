from datetime import datetime
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.models import TimestampMixin, SFUType


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
