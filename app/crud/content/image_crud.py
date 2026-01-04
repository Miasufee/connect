from app.crud import CrudBase
from app.models import Image, ImageGallery


class ImageCrud(CrudBase[Image]):
    def __init__(self):
        super().__init__(Image)

image_crud = ImageCrud()

class ImageGalleryCrud([ImageGallery]):
    def __init__(self):
        super().__init__(ImageGallery)

image_gallery_crud = ImageGalleryCrud()