from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, Form

from app.services.zawiya.zawiya_profile_service import zawiya_profile_service
from app.core.dependencies import RegularUser
from app.schemas.zawiya.zawiya_profile import ZawiyaProfile


router = APIRouter(prefix="/zawiya-profile")

@router.post("/update")
async def update_profile(
    zawiya_id: str = Form(...),
    sheik_name: str | None = Form(None),
    avatar: UploadFile | None = File(None),
    banner: UploadFile | None = File(None),
    owner: RegularUser = None,
):
    return await zawiya_profile_service.create_or_update(
        zawiya_id=zawiya_id,
        user_id=owner.id,
        avatar=avatar,
        banner=banner,
        sheik=sheik_name,
    )


@router.get("/get")
async def _get_zawiya_profile(payload: ZawiyaProfile):
    return await zawiya_profile_service.get_profile(
        zawiya_id=payload.zawiya_id
    )

@router.delete("/delete/")
async def _delete_profile(payload: ZawiyaProfile, owner: RegularUser = None):
    return await zawiya_profile_service.delete(payload.zawiya_id, owner.id)