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
