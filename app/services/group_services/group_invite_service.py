from beanie import PydanticObjectId

from app.crud.group_cruds.group_invite_crud import group_invite_crud
from app.crud.group_cruds.group_member_crud import group_member_crud
from app.models import InviteStatus


class GroupInviteService:
    @staticmethod
    async def invite_user(group_id, inviter_id, invitee_id):
        return await group_invite_crud.create(
            group_id=group_id,
            inviter_id=inviter_id,
            invitee_id=invitee_id,
        )

    @staticmethod
    async def accept_invite(
            group_id: PydanticObjectId,
            invitee_id: PydanticObjectId,
            status: InviteStatus
    ):
        group_invite = await group_invite_crud.update_by_filter(
            filters={
                "group_id": group_id,
                " invitee_id": invitee_id,
                "status": status.PENDING
            },
            update_data={
                "status": status.ACCEPTED
            }
        )

        await group_member_crud.add_member(
            group_id=group_invite.group_id,
            user_id=group_invite.inviter_id,
        )
