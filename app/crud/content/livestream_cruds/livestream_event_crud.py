from app.crud import CrudBase
from app.models import LiveStreamEvent


# ---------- Events ----------
class LiveStreamEventCrud(CrudBase[LiveStreamEvent]):
    def __init__(self):
        super().__init__(LiveStreamEvent)

event_crud = LiveStreamEventCrud()
