from app.crud import CrudBase
from app.models.group_models import GroupInvite


class GroupInviteCrud(CrudBase[GroupInvite]):
    """ GroupInvite Crud Management """
    def __init__(self):
        super().__init__(GroupInvite)

group_invite_crud = GroupInviteCrud()
