from app.crud import CrudBase
from app.models.interactions_models import PostReaction


class PostReactionCrud(CrudBase[PostReaction]):
    """ PostReaction Crud Management """
    def __init__(self):
        super().__init__(PostReaction)

post_reaction_crud = PostReactionCrud()