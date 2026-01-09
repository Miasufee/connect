from beanie import PydanticObjectId
from fastapi import APIRouter

from app.core.utils.dependencies import RegularUser
from app.models import InviteStatus
from app.services.group_services.group_invite_service import GroupInviteService

group_invite_router = APIRouter(prefix="/invite")

@group_invite_router.post("/user")
async def _invite_user(
        group_id: PydanticObjectId,
        invitee_id: PydanticObjectId,
        inviter_id: RegularUser = None,
):
    return await GroupInviteService.invite_user(
        group_id=group_id,
        inviter_id=inviter_id,
        invitee_id=invitee_id
    )

@group_invite_router.post("/accept/")
async def _accept_invite(
        group_id: PydanticObjectId,
        status: InviteStatus,
        invitee_id: RegularUser = None
):
    return await GroupInviteService.accept_invite(
        group_id=group_id,
        invitee_id=invitee_id.id,
        status=status
    )