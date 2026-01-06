from typing import Optional

from fastapi import APIRouter, status
from beanie import PydanticObjectId

from app.core.utils.dependencies import RegularUser
from app.models import VisibilityStatus
from app.services.group_services.group_service import GroupService

group_router = APIRouter(prefix="/groups", tags=["Groups"])


@group_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_group(
    zawiya_id: PydanticObjectId,
    title: str,
    description: Optional[str] = None,
    current_user: RegularUser = None,
):
    return await GroupService.create_group(
        zawiya_id=zawiya_id,
        creator_id=current_user.id,
        title=title,
        description=description,
    )

@group_router.patch("/{group_id}")
async def update_group(
    group_id: PydanticObjectId,
    title: Optional[str] = None,
    description: Optional[str] = None,
    current_user: RegularUser = None,
):
    return await GroupService.update_group(
        group_id=group_id,
        actor_id=current_user.id,
        title=title,
        description=description,
    )

@group_router.patch("/{group_id}/visibility")
async def change_visibility(
    group_id: PydanticObjectId,
    visibility: VisibilityStatus,
    current_user: RegularUser = None,
):
    return await GroupService.change_visibility(
        group_id=group_id,
        actor_id=current_user.id,
        visibility=visibility,
    )

@group_router.delete("/{group_id}")
async def delete_group(
    group_id: PydanticObjectId,
    current_user: RegularUser = None,
):
    await GroupService.delete_group(
        group_id=group_id,
        actor_id=current_user.id,
    )
    return {"success": True}

@group_router.post("/{group_id}/restore")
async def restore_group(
    group_id: PydanticObjectId,
    current_user: RegularUser = None,
):
    await GroupService.restore_group(
        group_id=group_id,
        actor_id=current_user.id,
    )