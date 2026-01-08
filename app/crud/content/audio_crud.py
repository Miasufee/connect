from app.crud import CrudBase
from app.models import Audio


class AudioCrud(CrudBase[Audio]):
    """ Audio Crud Management"""
    def __init__(self):
        super().__init__(Audio)

audio_crud = AudioCrud()