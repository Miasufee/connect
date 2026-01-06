from app.crud import CrudBase
from app.crud.group_cruds.group_member_crud import group_member_crud

from app.models import GroupRole
from app.models.group_models import Group


class GroupCrud(CrudBase[Group]):
    def __init__(self):
        super().__init__(Group)

    async def create_group(self, *, zawiya_id, user_id, title, description):
        group = await self.create(
            zawiya_id=zawiya_id,
            user_id=user_id,
            title=title,
            description=description,
            created_by=user_id,
        )

        await (
            group_member_crud.add_member(
            group_id=group.id,
            user_id=user_id,
            role=GroupRole.OWNER,
            can_post=True,
            can_stream=True,
        ))

        return group

group_crud = GroupCrud()