from typing import Optional, List

from beanie import PydanticObjectId

from app.crud import CrudBase
from app.models import GroupRole
from app.models.group_models import GroupMember


class GroupMemberCrud(CrudBase[GroupMember]):
    def __init__(self):
        super().__init__(GroupMember)

    async def create_group_owner(self, group_id: PydanticObjectId, created_by: PydanticObjectId):
        return await self.create(
            group_id=group_id,
            user_id=created_by,
            group_role=GroupRole.OWNER,
            can_post=True,
            can_stream=True
        )

    async def set_group_permissions(
        self,
        group_id: PydanticObjectId,
        user_id: PydanticObjectId,
        *,
        is_admin: Optional[bool] = None,
        can_post: Optional[bool] = None,
        can_stream: Optional[bool] = None,
    ) -> Optional[GroupMember]:
        member = await self.get_one(
            filters={"group_id": group_id, "user_id": user_id}
        )
        if not member:
            return None

        await member.set(
            {
                "is_admin": is_admin,
                "can_post": can_post,
                "can_stream": can_stream,
            }
        )
        return member

    async def set_group_role(
            self,
            group_id: PydanticObjectId,
            user_id: PydanticObjectId,
            group_role: GroupRole
    ):
        return await self.update_by_filter(
            filters={
            "group_id": group_id,
            "user_id": user_id,
        },
            update_data={"group_role": group_role}
        )
    async def list_members(
        self,
        group_id: PydanticObjectId,
    ) -> List[GroupMember]:
        return await self.get_multi(
            {"group_id": group_id}
        )

    async def is_member(
        self,
        group_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ) -> bool:
        return await self.get_one(
            filters={"group_id": group_id, "user_id": user_id}
        ) is not None



    async def is_group_owner(
            self,
            group_id: PydanticObjectId,
            user_id: PydanticObjectId,
    ):
        return await self.get_one(
            filters={
                "group_id": group_id,
                "user_id": user_id,
                "group_role": GroupRole.OWNER
            }
        ) is not None

    async def is_group_admin(
        self,
        group_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ) -> bool:
        return await self.get_one(
            filters={
                "group_id": group_id,
                "user_id": user_id,
                "group_role": GroupRole.ADMIN,
            }
        ) is not None

    async def is_group_member(
            self,
            group_id: PydanticObjectId,
            user_id: PydanticObjectId,
    ):
        return await self.get_one(
            filters={
                "group_id": group_id,
                "user_id": user_id,
                "group_role": GroupRole.MEMBER
            }
        ) is not None

    async def add_member_or_join(
            self,
            group_id: PydanticObjectId,
            member_id: PydanticObjectId
    ):
        return await self.create(group_id=group_id, user_id=member_id)

    async def add_admin_member(
            self,
            group_id: PydanticObjectId,
            member_id: PydanticObjectId,
            group_role: GroupRole = GroupRole.ADMIN
    ):
        return await self.create(
            group_id=group_id,
            user_id=member_id,
            group_role=group_role
        )

    async def remove_or_leave(
            self,
            group_id: PydanticObjectId,
            user_id: PydanticObjectId
    ):
        return await self.delete_by_filter(
            filters={"group_id": group_id, "user_id": user_id}
        )

    async def count_members(
        self,
        group_id: PydanticObjectId,
    ) -> int:
        return await self.count(filters={"group_id": group_id})


    async def update_group_role(
        self,
        group_id: PydanticObjectId,
        user_id: PydanticObjectId,
        role: GroupRole,
    ) -> Optional[GroupMember]:
        return await self.update_by_filter(
            filters={"group_id": group_id, "user_id": user_id},
            update_data={"group_role": role},
        )


    async def update_permissions(
        self,
        group_id: PydanticObjectId,
        user_id: PydanticObjectId,
        *,
        can_post: Optional[bool] = None,
        can_stream: Optional[bool] = None,
    ) -> Optional[GroupMember]:
        return await self.update_by_filter(
            filters={"group_id": group_id, "user_id": user_id},
            update_data={
                "can_post": can_post,
                "can_stream": can_stream,
            },
        )


group_member_crud = GroupMemberCrud()