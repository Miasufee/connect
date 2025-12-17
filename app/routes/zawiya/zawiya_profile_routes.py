from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, Form, Request

from app.services.zawiya.zawiya_profile_service import zawiya_profile_service
from app.core.utils.dependencies import RegularUser
from app.schemas.zawiya.zawiya_profile_schema import ZawiyaProfile
import logging

router = APIRouter(prefix="/zawiya-profile")


logger = logging.getLogger("zawiya.profile")

@router.patch("/update")
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
async def _get_zawiya_profile(
    payload: ZawiyaProfile,
    request: Request,
):
    return await zawiya_profile_service.get(
        zawiya_id=payload.zawiya_id,
        request=request,
    )


@router.delete("/delete/")
async def _delete_profile(payload: ZawiyaProfile, owner: RegularUser = None):
    return await zawiya_profile_service.delete(zawiya_id=payload.zawiya_id, user_id=owner.id)