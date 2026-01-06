from app.crud.group_cruds.group_invite_crud import group_invite_crud
from app.crud.group_cruds.group_member_crud import group_member_crud
from app.models import InviteStatus
from app.models.group_models import GroupInvite


class GroupInviteService:
    @staticmethod
    async def invite_user(group_id, inviter_id, invitee_id):
        return await group_invite_crud.create(
            group_id=group_id,
            inviter_id=inviter_id,
            invitee_id=invitee_id,
        )

    @staticmethod
    async def accept_invite(invite: GroupInvite):
        invite.status = InviteStatus.ACCEPTED
        await invite.save()

        await group_member_crud.add_member(
            group_id=invite.group_id,
            user_id=invite.invitee_id,
        )
