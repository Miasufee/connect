from typing import Optional
from pydantic import BaseModel, Field
from beanie import PydanticObjectId
from app.models.enums import ParticipantRole, StreamStatus, StreamType, VisibilityStatus

# --------------------- Stream ---------------------
class StreamCreateSchema(BaseModel):
    title: str = Field(min_length=5, max_length=500)
    description: Optional[str] = None
    visibility: VisibilityStatus = VisibilityStatus.PUBLIC
    stream_type: StreamType = StreamType.ONE_TO_MANY
    is_recorded: bool = True

class StreamResponseSchema(BaseModel):
    id: PydanticObjectId
    title: str
    description: Optional[str]
    streamer_id: PydanticObjectId
    zawiya_id: PydanticObjectId
    status: StreamStatus
    visibility: VisibilityStatus
    stream_type: StreamType
    is_recorded: bool
    started_at: Optional[str]
    ended_at: Optional[str]


# --------------------- Participant ---------------------
class ParticipantAddSchema(BaseModel):
    user_id: PydanticObjectId
    role: ParticipantRole = ParticipantRole.VIEWER

class ParticipantResponseSchema(BaseModel):
    id: PydanticObjectId
    stream_id: PydanticObjectId
    user_id: PydanticObjectId
    role: ParticipantRole


# --------------------- Analytics ---------------------
class AnalyticsResponseSchema(BaseModel):
    stream_id: PydanticObjectId
    viewers: int
    likes: int
