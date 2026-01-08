from app.crud import CrudBase
from app.models import Video


class VideoCrud(CrudBase[Video]):
    """ Video Crud Management """
    def __init__(self):
        super().__init__(Video)

video_crud = VideoCrud()