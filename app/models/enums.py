from enum import Enum


class VideoStatus(str, Enum):
    Uploading = "Uploading"
    Processing = "Processing"
    Complete = "Complete"
    Error = "Error"


class LiveStreamStatus(str, Enum):
    Waiting = "Waiting"
    Live = "Live"
    Ended = "Ended"
    Cancelled = "Cancelled"
    Error = "Error"


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
