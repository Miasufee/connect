from app.crud import CrudBase
from app.models import WebRTCPeer


# ---------- WebRTCPeer ----------
class WebRTCPeerCrud(CrudBase[WebRTCPeer]):
    """ WebRTCPeer Crud Management """
    def __init__(self):
        super().__init__(WebRTCPeer)

webrtc_peer_crud = WebRTCPeerCrud()
