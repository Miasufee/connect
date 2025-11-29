from app.crud import CrudBase
from app.models.content_models import Video


class VideoCrud(CrudBase[Video]):
    def  __init__(self):
        super().__init__(Video)

video_crud = VideoCrud()