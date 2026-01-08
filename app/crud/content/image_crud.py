from app.crud import CrudBase
from app.models import Image, ImageGallery


class ImageCrud(CrudBase[Image]):
    """ Image Crud Management"""
    def __init__(self):
        super().__init__(Image)

image_crud = ImageCrud()

class ImageGalleryCrud([ImageGallery]):
    """ ImageGallery Crud Management """
    def __init__(self):
        super().__init__(ImageGallery)

image_gallery_crud = ImageGalleryCrud()