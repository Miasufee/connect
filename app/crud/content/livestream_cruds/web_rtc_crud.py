from app.crud import CrudBase
from app.models import WebRTCSession


# ---------- WebRTCSession ----------
class WebRTCSessionCrud(CrudBase[WebRTCSession]):
    """ WebRTCSession Crud Management """
    def __init__(self):
        super().__init__(WebRTCSession)

webrtc_session_crud = WebRTCSessionCrud()