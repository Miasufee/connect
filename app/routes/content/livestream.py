from fastapi import APIRouter, HTTPException
from typing import List, Optional
from beanie import PydanticObjectId

from app.models import ParticipantRole
from app.schemas.livestream.livestream import StreamResponseSchema, StreamCreateSchema, ParticipantResponseSchema, \
    ParticipantAddSchema, AnalyticsResponseSchema
from app.services.contents.livestream_service.livestream_service import LiveStreamService

router = APIRouter(prefix="/streams", tags=["LiveStreams"])

# --------------------- Stream Endpoints ---------------------

@router.post("/", response_model=StreamResponseSchema)
async def create_stream(payload: StreamCreateSchema, streamer_id: PydanticObjectId, zawiya_id: PydanticObjectId):
    stream = await LiveStreamService.create_stream(
        streamer_id=streamer_id,
        zawiya_id=zawiya_id,
        title=payload.title,
        description=payload.description,
        stream_type=payload.stream_type,
        visibility=payload.visibility,
        is_recorded=payload.is_recorded,
    )
    return stream

@router.post("/{stream_id}/start", response_model=StreamResponseSchema)
async def start_stream(stream_id: PydanticObjectId):
    stream = await LiveStreamService.start_stream(stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")
    return stream

@router.post("/{stream_id}/end", response_model=StreamResponseSchema)
async def end_stream(stream_id: PydanticObjectId):
    stream = await LiveStreamService.end_stream(stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")
    return stream

@router.get("/active", response_model=List[StreamResponseSchema])
async def get_active_streams(zawiya_id: Optional[PydanticObjectId] = None):
    streams = await LiveStreamService.get_active_streams(zawiya_id)
    return streams


# --------------------- Participants Endpoints ---------------------

@router.post("/{stream_id}/participants", response_model=ParticipantResponseSchema)
async def add_participant(stream_id: PydanticObjectId, payload: ParticipantAddSchema):
    participant = await LiveStreamService.add_participant(
        stream_id=stream_id,
        user_id=payload.user_id,
        role=payload.role
    )
    return participant

@router.post("/{stream_id}/participants/{user_id}/promote", response_model=ParticipantResponseSchema)
async def promote_participant(stream_id: PydanticObjectId, user_id: PydanticObjectId, role: ParticipantRole):
    participant = await LiveStreamService.promote_participant(stream_id, user_id, role)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    return participant

@router.delete("/{stream_id}/participants/{user_id}", response_model=dict)
async def remove_participant(stream_id: PydanticObjectId, user_id: PydanticObjectId):
    await LiveStreamService.remove_participant(stream_id, user_id)
    return {"status": "removed"}


# --------------------- Analytics Endpoints ---------------------

@router.post("/{stream_id}/viewers")
async def increment_viewers(stream_id: PydanticObjectId, count: int = 1):
    await LiveStreamService.increment_viewers(stream_id, count)
    return {"status": "ok"}

@router.post("/{stream_id}/likes")
async def add_like(stream_id: PydanticObjectId, count: int = 1):
    await LiveStreamService.add_like(stream_id, count)
    return {"status": "ok"}

@router.get("/{stream_id}/analytics", response_model=AnalyticsResponseSchema)
async def get_analytics(stream_id: PydanticObjectId):
    analytics = await LiveStreamService.get_analytics(stream_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    return analytics
