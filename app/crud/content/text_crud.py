

from app.crud import CrudBase
from app.models import TextPost


class TextCrud(CrudBase[TextPost]):
    """ Text Crud Management """
    def __init__(self):
        super().__init__(TextPost)

text_post_crud = TextCrud()