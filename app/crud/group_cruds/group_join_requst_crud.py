from app.crud import CrudBase
from app.models.group_models import GroupJoinRequest


class GroupJoinRequestCrud(CrudBase[GroupJoinRequest]):
    """ GroupJoinRequest Crud Management """
    def __init__(self):
        super().__init__(GroupJoinRequest)

group_join_request_crud = GroupJoinRequestCrud()