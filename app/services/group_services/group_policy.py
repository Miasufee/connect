from app.crud.group_cruds.group_member_crud import group_member_crud
from app.models import GroupRole


class GroupPolicy:
    @staticmethod
    async def has_role(group_id, user_id, *roles: GroupRole) -> bool:
        member = await group_member_crud.get_member(group_id, user_id)
        return bool(member and member.group_role in roles)

    @staticmethod
    async def is_group_owner(group_id, user_id) -> bool:
        return await GroupPolicy.has_role(
            group_id, user_id, GroupRole.OWNER
        )

    @staticmethod
    async def is_group_admin(group_id, user_id) -> bool:
        return await GroupPolicy.has_role(
            group_id, user_id, GroupRole.ADMIN, GroupRole.OWNER
        )
