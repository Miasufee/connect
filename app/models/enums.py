from enum import Enum


class VisibilityStatus(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"

class StreamStatus(str, Enum):
    CREATED = "created"
    LIVE = "live"
    ENDED = "ended"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"

class StreamType(str, Enum):
    ONE_TO_MANY = "one_to_many"
    GROUP = "group"

class RecordingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoVisibility(str, Enum):
    PRIVATE = "private"
    UNLISTED = "unlisted"
    PUBLIC = "public"

class VideoStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class ParticipantRole(str, Enum):
    OWNER = "owner"
    CO_HOST =  "co_host"
    SPEAKER = "speaker"
    VIEWER = "viewer"

class LiveStreamEventType(str, Enum):
    mute = "mute"
    unmute = "unmute"
    kick = "kick"
    ban = "ban"
    promote = "promote"
    demote = "demote"
    end_stream = "end_stream"

class ContentType(str, Enum):
    VIDEO = "video"
    LIVESTREAM = "livestream"
    POST = "post"
    AUDIO = "audio"
    IMAGE = "image"

class SFUType(str, Enum):
    MEDIA_SOUP = "media-soup"
    LIVE_KIT = "livekit"
    JANUS = "janus"
    CUSTOM = "custom"