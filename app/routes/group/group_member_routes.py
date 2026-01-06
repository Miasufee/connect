from fastapi import APIRouter, HTTPException, status
from beanie import PydanticObjectId

from app.core.utils.dependencies import RegularUser
from app.services.group_services.group_member_service import GroupMemberService

group_member_router = APIRouter(prefix="/groups/{group_id}/members", tags=["Group Members"])

@group_member_router.post("/join", status_code=status.HTTP_201_CREATED)
async def join_group(
    group_id: PydanticObjectId,
    current_user: RegularUser = None,
):
    result = await GroupMemberService.join_group(
        group_id=group_id,
        user_id=current_user.id,
    )

    if not result:
        raise HTTPException(status_code=400, detail="Already a member")

    return result

@group_member_router.post("/leave")
async def leave_group(
    group_id: PydanticObjectId,
    current_user: RegularUser = None,
):
    await GroupMemberService.leave_group(
        group_id=group_id,
        user_id=current_user.id,
    )
    return {"success": True}

@group_member_router.post("/{user_id}/promote")
async def promote_to_admin(
    group_id: PydanticObjectId,
    user_id: PydanticObjectId,
    current_user: RegularUser = None,
):
    return await GroupMemberService.promote_to_admin(
        group_id=group_id,
        actor_id=current_user.id,
        target_user_id=user_id,
    )

@group_member_router.post("/{user_id}/demote")
async def demote_admin(
    group_id: PydanticObjectId,
    user_id: PydanticObjectId,
    current_user: RegularUser = None,
):
    return await GroupMemberService.demote_admin(
        group_id=group_id,
        actor_id=current_user.id,
        target_user_id=user_id,
    )

@group_member_router.patch("/{user_id}/permissions")
async def update_member_permissions(
    group_id: PydanticObjectId,
    user_id: PydanticObjectId,
    can_post: bool | None = None,
    can_stream: bool | None = None,
    current_user: RegularUser = None,
):
    return await GroupMemberService.update_permissions(
        group_id=group_id,
        actor_id=current_user.id,
        target_user_id=user_id,
        can_post=can_post,
        can_stream=can_stream,
    )