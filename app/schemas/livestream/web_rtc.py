from pydantic import BaseModel
from beanie import PydanticObjectId

class WebRTCSessionCreateSchema(BaseModel):
    sfu_type: str  # e.g., "media-soup", "janus"
    sfu_room_id: str

class WebRTCSessionResponseSchema(BaseModel):
    id: PydanticObjectId
    stream_id: PydanticObjectId
    sfu_type: str
    sfu_room_id: str

class WebRTCPeerCreateSchema(BaseModel):
    user_id: PydanticObjectId
    peer_id: str

class WebRTCPeerResponseSchema(BaseModel):
    id: PydanticObjectId
    session_id: PydanticObjectId
    user_id: PydanticObjectId
    peer_id: str
