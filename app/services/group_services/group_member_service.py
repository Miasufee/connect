from beanie import PydanticObjectId

from app.core.response.exceptions import Exceptions
from app.crud.group_cruds.group_member_crud import group_member_crud
from app.models import GroupRole
from app.services.group_services.group_policy import GroupPolicy


class GroupMemberService:
    @staticmethod
    async def join_group(
        *,
        group_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ):
        if await group_member_crud.get_member(group_id, user_id):
            return None

        return await group_member_crud.add_member(
            group_id=group_id,
            user_id=user_id,
        )

    @staticmethod
    async def leave_group(
        *,
        group_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ):
        return await group_member_crud.delete_by_filter(
            filters={"group_id": group_id, "user_id": user_id}
        )

    @staticmethod
    async def promote_to_admin(
        *,
        group_id: PydanticObjectId,
        actor_id: PydanticObjectId,
        target_user_id: PydanticObjectId,
    ):
        if not await GroupPolicy.is_group_owner(group_id, actor_id):
            raise Exceptions.forbidden(detail="Only owner can promote admins")

        return await group_member_crud.update_role(
            group_id,
            target_user_id,
            GroupRole.ADMIN,
        )

    @staticmethod
    async def demote_admin(
        *,
        group_id: PydanticObjectId,
        actor_id: PydanticObjectId,
        target_user_id: PydanticObjectId,
    ):
        if not await GroupPolicy.is_group_owner(group_id, actor_id):
            raise Exceptions.forbidden(detail="Only owner can demote admins")

        return await group_member_crud.update_role(
            group_id,
            target_user_id,
            GroupRole.MEMBER,
        )

    @staticmethod
    async def update_permissions(
        *,
        group_id: PydanticObjectId,
        actor_id: PydanticObjectId,
        target_user_id: PydanticObjectId,
        can_post: bool | None = None,
        can_stream: bool | None = None,
    ):
        if not await GroupPolicy.is_group_admin(group_id, actor_id):
            raise Exceptions.forbidden(detail="Admins only")

        return await group_member_crud.update_permissions(
            group_id,
            target_user_id,
            can_post=can_post,
            can_stream=can_stream,
        )
