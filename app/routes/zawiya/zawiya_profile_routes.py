from fastapi import APIRouter

from app.core.dependencies import RegularUser
from app.core.response.exceptions import Exceptions
from app.crud.zawiya_cruds import zawiya_profile_crud
from app.crud.zawiya_cruds.zawiya_admin_crud import zawiya_admin_crud
from app.schemas.zawiya.zawiya_profile import ZawiyaProfile, ZawiyaProfileCreate

router = APIRouter(prefix="/zawiya-profile")

@router.post("/create/")
async def _create_or_update_profile(payload: ZawiyaProfileCreate, owner: RegularUser = None):
    verify_owner = await zawiya_admin_crud.is_owner(
        user_id=owner.id,
        zawiya_id=payload.zawiya_id
    )
    if not verify_owner:
        raise Exceptions.permission_denied(detail="your not the owner")
    return await zawiya_profile_crud.create_or_update_profile(
        zawiya_id=payload.zawiya_id,
        avatar=payload.avatar,
        banner=payload.banner,
        sheik=payload.sheik_name
    )

@router.get("/get")
async def _get_zawiya_profile(payload: ZawiyaProfile):
    return await zawiya_profile_crud.get_profile(
        zawiya_id=payload.zawiya_id
    )

@router.delete("/delete/")
async def _delete_profile(payload: ZawiyaProfile, owner: RegularUser = None):
    verify_owner = await zawiya_admin_crud.is_owner(
        user_id=owner.id,
        zawiya_id=payload.zawiya_id
    )
    if not verify_owner:
        raise Exceptions.permission_denied(detail="your not the owner")
    return await zawiya_profile_crud.delete_zawiya_profile(
        zawiya_id=payload.zawiya_id
    )