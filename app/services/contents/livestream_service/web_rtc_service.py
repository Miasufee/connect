from beanie import PydanticObjectId

from app.crud.content.livestream_cruds.web_rtc_crud import webrtc_session_crud
from app.crud.content.livestream_cruds.web_rtc_peer_crud import webrtc_peer_crud
from app.models import WebRTCSession, WebRTCPeer


class WebRTCSessionService:

    # --------------------- WebRTC Sessions ---------------------
    @staticmethod
    async def create_webrtc_session(stream_id: PydanticObjectId, sfu_type: str, sfu_room_id: str) -> WebRTCSession:
        """Create a WebRTC session for the SFU."""
        return await webrtc_session_crud.create(stream_id=stream_id, sfu_type=sfu_type, sfu_room_id=sfu_room_id)

    @staticmethod
    async def add_webrtc_peer(session_id: PydanticObjectId, user_id: PydanticObjectId, peer_id: str) -> WebRTCPeer:
        """Register a new peer in the WebRTC session."""
        return await webrtc_peer_crud.create(session_id=session_id, user_id=user_id, peer_id=peer_id)

webrtc_session_service = WebRTCSessionService()