from app.crud import CrudBase
from app.models import Audio


class AudioCrud(CrudBase[Audio]):
    def __init__(self):
        super().__init__(Audio)

audio_crud = AudioCrud()