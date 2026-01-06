from typing import Optional

from beanie import PydanticObjectId

from app.crud.group_cruds.group_crud import group_crud
from app.crud.group_cruds.group_member_crud import group_member_crud
from app.models import GroupRole, VisibilityStatus
from app.services.group_services.group_policy import GroupPolicy


class GroupService:
    @staticmethod
    async def create_group(
        *,
        zawiya_id: PydanticObjectId,
        creator_id: PydanticObjectId,
        title: str,
        description: Optional[str] = None,
    ):
        group = await group_crud.create(
            zawiya_id=zawiya_id,
            user_id=creator_id,
            title=title,
            description=description,
            created_by=creator_id,
        )

        # creator becomes OWNER
        await group_member_crud.add_member(
            group_id=group.id,
            user_id=creator_id,
            role=GroupRole.OWNER,
            can_post=True,
            can_stream=True,
        )

        return group

    @staticmethod
    async def update_group(
        *,
        group_id: PydanticObjectId,
        actor_id: PydanticObjectId,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ):
        if not await GroupPolicy.is_group_admin(group_id, actor_id):
            raise PermissionError("Not allowed")

        return await group_crud.update(
            group_id,
            {"title": title, "description": description},
        )

    @staticmethod
    async def change_visibility(
        *,
        group_id: PydanticObjectId,
        actor_id: PydanticObjectId,
        visibility: VisibilityStatus,
    ):
        if not await GroupPolicy.is_group_owner(group_id, actor_id):
            raise PermissionError("Only owner can change visibility")

        return await group_crud.update(group_id, {"visibility": visibility})

    @staticmethod
    async def delete_group(
        *,
        group_id: PydanticObjectId,
        actor_id: PydanticObjectId,
    ) -> bool:
        if not await GroupPolicy.is_group_owner(group_id, actor_id):
            raise PermissionError("Only owner can delete group")

        return await group_crud.soft_delete(group_id)

    @staticmethod
    async def restore_group(
        *,
        group_id: PydanticObjectId,
        actor_id: PydanticObjectId,
    ) -> bool:
        if not await GroupPolicy.is_group_owner(group_id, actor_id):
            raise PermissionError("Only owner can restore group")

        return await group_crud.restore(group_id)
