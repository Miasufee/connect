from app.crud import CrudBase
from app.models import (
    LiveStream,
    LiveStreamParticipant,
    WebRTCSession,
    WebRTCPeer,
    Recording,
    StreamAnalytics,
    LiveStreamEvent,
)


# ---------- LiveStream ----------
class LiveStreamCrud(CrudBase[LiveStream]):
    def __init__(self):
        super().__init__(LiveStream)

live_stream_crud = LiveStreamCrud()


# ---------- Participant ----------
class LiveStreamParticipantCrud(CrudBase[LiveStreamParticipant]):
    def __init__(self):
        super().__init__(LiveStreamParticipant)

participant_crud = LiveStreamParticipantCrud()


# ---------- WebRTCSession ----------
class WebRTCSessionCrud(CrudBase[WebRTCSession]):
    def __init__(self):
        super().__init__(WebRTCSession)

webrtc_session_crud = WebRTCSessionCrud()


# ---------- WebRTCPeer ----------
class WebRTCPeerCrud(CrudBase[WebRTCPeer]):
    def __init__(self):
        super().__init__(WebRTCPeer)

webrtc_peer_crud = WebRTCPeerCrud()


# ---------- Recording ----------
class RecordingCrud(CrudBase[Recording]):
    def __init__(self):
        super().__init__(Recording)

recording_crud = RecordingCrud()


# ---------- Analytics ----------
class StreamAnalyticsCrud(CrudBase[StreamAnalytics]):
    def __init__(self):
        super().__init__(StreamAnalytics)

analytics_crud = StreamAnalyticsCrud()


# ---------- Events ----------
class LiveStreamEventCrud(CrudBase[LiveStreamEvent]):
    def __init__(self):
        super().__init__(LiveStreamEvent)

event_crud = LiveStreamEventCrud()
