from beanie import PydanticObjectId
from fastapi import APIRouter, UploadFile

from app.core.utils.dependencies import RegularUser
from app.services.group_services.group_profile_service import GroupProfileService

group_profile_router = APIRouter(tags=["group_profile"])

@group_profile_router.put("/update/profile")
async def _update_group_profile(
        profile_id: PydanticObjectId,
        averter: UploadFile,
        user_id: RegularUser = None
):
    return await GroupProfileService.set_group_profile(
        group_id=profile_id,
        user_id=user_id.id,
        avatar=averter,
    )

@group_profile_router.get("/get/profile")
async def _get_group_profile(
        group_id: PydanticObjectId
):
    return await GroupProfileService.get_group_profile(
        group_id=group_id
    )

@group_profile_router.delete("/delete/profile/")
async def _delete_group_profile(
        group_id: PydanticObjectId,
        user_id: RegularUser = None
):
    return GroupProfileService.delete_group_profile(
        group_id=group_id,
        user_id=user_id.id
    )