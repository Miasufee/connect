from fastapi import APIRouter
from beanie import PydanticObjectId
from typing import List

from app.schemas.livestream.web_rtc_schema import WebRTCSessionResponseSchema, WebRTCSessionCreateSchema, \
    WebRTCPeerResponseSchema, WebRTCPeerCreateSchema
from app.services.contents.livestream_service.web_rtc_peer_service import web_rtc_peer_service
from app.services.contents.livestream_service.web_rtc_service import webrtc_session_service

webrtc_router = APIRouter(prefix="/webrtc", tags=["WebRTC"])


# --------------------- SFU Session Endpoints ---------------------
@webrtc_router.post("/sessions/{stream_id}", response_model=WebRTCSessionResponseSchema)
async def create_webrtc_session(stream_id: PydanticObjectId, payload: WebRTCSessionCreateSchema):
    session = await webrtc_session_service.create_webrtc_session(
        stream_id=stream_id,
        sfu_type=payload.sfu_type,
        sfu_room_id=payload.sfu_room_id
    )
    return session

@webrtc_router.get("/sessions/{stream_id}", response_model=List[WebRTCSessionResponseSchema])
async def get_sessions(stream_id: PydanticObjectId):
    sessions = await webrtc_session_service.get_sessions(stream_id)
    return sessions


# --------------------- Peer Endpoints ---------------------
@webrtc_router.post("/sessions/{session_id}/peers", response_model=WebRTCPeerResponseSchema)
async def add_webrtc_peer(session_id: PydanticObjectId, payload: WebRTCPeerCreateSchema):
    peer = await web_rtc_peer_service.add_webrtc_peer(
        session_id=session_id,
        user_id=payload.user_id,
        peer_id=payload.peer_id
    )
    return peer

@webrtc_router.get("/sessions/{session_id}/peers", response_model=List[WebRTCPeerResponseSchema])
async def get_peers(session_id: PydanticObjectId):
    peers = await web_rtc_peer_service.get_peers(session_id)
    return peers

@webrtc_router.delete("/sessions/{session_id}/peers/{peer_id}", response_model=dict)
async def remove_peer(session_id: PydanticObjectId, peer_id: str):
    await web_rtc_peer_service.remove_webrtc_peer(session_id, peer_id)
    return {"status": "removed"}
