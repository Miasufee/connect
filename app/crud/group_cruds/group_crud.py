from app.crud import CrudBase
from app.models.group_models import Group


class GroupCrud(CrudBase[Group]):
    """ Group Crud Management """
    def __init__(self):
        super().__init__(Group)

group_crud = GroupCrud()