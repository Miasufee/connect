from app.crud import CrudBase
from app.models import Recording


# ---------- Recording ----------
class RecordingCrud(CrudBase[Recording]):
    """ Recording Crud Management """
    def __init__(self):
        super().__init__(Recording)

recording_crud = RecordingCrud()
