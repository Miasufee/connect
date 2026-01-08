# ---------- Participant ----------
from app.crud import CrudBase
from app.models import LiveStreamParticipant


class LiveStreamParticipantCrud(CrudBase[LiveStreamParticipant]):
    """ LiveStreamParticipant Crud Management """
    def __init__(self):
        super().__init__(LiveStreamParticipant)

participant_crud = LiveStreamParticipantCrud()