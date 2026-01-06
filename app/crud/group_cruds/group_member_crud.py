from typing import Optional

from app.crud import CrudBase
from app.models import GroupRole
from app.models.group_models import GroupMember


class GroupMemberCrud(CrudBase[GroupMember]):
    def __init__(self):
        super().__init__(GroupMember)

    async def get_member(self, group_id, user_id):
        return await self.get_one(
            filters={"group_id": group_id, "user_id": user_id}
        )

    async def add_member(
        self,
        group_id,
        user_id,
        role: GroupRole = GroupRole.MEMBER,
        *,
        can_post: bool = False,
        can_stream: bool = False,
    ):
        return await self.create(
            group_id=group_id,
            user_id=user_id,
            group_role=role,
            can_post=can_post,
            can_stream=can_stream,
        )

    async def update_role(self, group_id, user_id, role: GroupRole):
        return await self.update_by_filter(
            filters={"group_id": group_id, "user_id": user_id},
            update_data={"group_role": role},
        )

    async def update_permissions(
        self,
        group_id,
        user_id,
        *,
        can_post: Optional[bool] = None,
        can_stream: Optional[bool] = None,
    ):
        data = {k: v for k, v in {
            "can_post": can_post,
            "can_stream": can_stream,
        }.items() if v is not None}

        return await self.update_by_filter(
            filters={"group_id": group_id, "user_id": user_id},
            update_data=data,
        )

group_member_crud = GroupMemberCrud()