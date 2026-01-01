from beanie import PydanticObjectId

from app.crud.livestream_cruds.web_rtc_peer_crud import webrtc_peer_crud
from app.models import WebRTCPeer


class WebRTCPeerService:
    @staticmethod
    async def add_webrtc_peer(session_id: PydanticObjectId, user_id: PydanticObjectId, peer_id: str) -> WebRTCPeer:
        """Register a new peer in the WebRTC session."""
        return await webrtc_peer_crud.create(session_id=session_id, user_id=user_id, peer_id=peer_id)

    @staticmethod
    async def get_peers(session_id: PydanticObjectId):
        pass

    @staticmethod
    async def remove_webrtc_peer(session_id: PydanticObjectId):
        pass

web_rtc_peer_service = WebRTCPeerService()
