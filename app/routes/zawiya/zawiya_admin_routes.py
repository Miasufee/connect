from fastapi import APIRouter, Body

from app.core.utils.dependencies import RegularUser
from app.schemas.zawiya.zawiya_admin_schema import ZawiyaAdmin, ZawiyaAdminCreate, ZawiyaRoleUpdate, AdminRemove
from app.services.zawiya.zawiya_admin_service import zawiya_admin_service

router = APIRouter()

@router.post("/add/zawiya/admin")
async def _add_admin(payload: ZawiyaAdminCreate = Body(...), owner: RegularUser = None):
    return await zawiya_admin_service.add_admin(
        owner_id=owner.id,
        user_id=payload.user_id,
        zawiya_id=payload.zawiya_id,
        role=payload.role
    )

@router.post("/update/zawiya/admin")
async def _update_admin_role(payload: ZawiyaRoleUpdate = Body(...), owner: RegularUser = None):
    return await zawiya_admin_service.update_role(
        owner_id=owner.id,
        admin_id=payload.admin_id,
        zawiya_id=payload.zawiya_id,
        new_role=payload.role
    )

@router.get("/remove/zawiya/admin")
async def _remove_admin(payload: AdminRemove = Body(...), owner: RegularUser = None):
    return await zawiya_admin_service.remove_admin(
        owner_id=owner.id,
        admin_id=payload.admin_id,
        zawiya_id=payload.zawiya_id
    )

@router.get("/list/zawiya/admins")
async def _get_admins(payload: ZawiyaAdmin):
    return await zawiya_admin_service.list_admins(zawiya_id=payload.zawiya_id)