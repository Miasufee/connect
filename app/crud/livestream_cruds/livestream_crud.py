from app.crud import CrudBase
from app.models import LiveStream

# ---------- LiveStream ----------
class LiveStreamCrud(CrudBase[LiveStream]):
    def __init__(self):
        super().__init__(LiveStream)

live_stream_crud = LiveStreamCrud()