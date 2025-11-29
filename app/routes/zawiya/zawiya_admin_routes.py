from fastapi import APIRouter, Body

from app.core.dependencies import RegularUser
from app.crud.zawiya_cruds.zawiya_admin_crud import zawiya_admin_crud
from app.schemas.zawiya.zawiya_admin import ZawiyaAdmin, ZawiyaAdminCreate, ZawiyaRoleUpdate, AdminRemove

router = APIRouter()

@router.post("/add/zawiya/admin")
async def _add_admin(payload: ZawiyaAdminCreate = Body(...), owner: RegularUser = None):
    return await zawiya_admin_crud.add_admin(
        owner_id=owner.id,
        user_id=payload.user_id,
        zawiya_id=payload.zawiya_id,
        role=payload.role
    )

@router.post("/update/zawiya/admin")
async def _update_admin_role(payload: ZawiyaRoleUpdate = Body(...), owner: RegularUser = None):
    return await zawiya_admin_crud.update_role(
        owner_id=owner.id,
        admin_id=payload.admin_id,
        zawiya_id=payload.zawiya_id,
        new_role=payload.role
    )

@router.get("/remove/zawiya/admin")
async def _remove_admin(payload: AdminRemove = Body(...), owner: RegularUser = None):
    return await zawiya_admin_crud.remove_admin(
        owner_id=owner.id,
        admin_id=payload.admin_id,
        zawiya_id=payload.zawiya_id
    )

@router.get("/list/zawiya/admins")
async def _get_admins(payload: ZawiyaAdmin):
    return await zawiya_admin_crud.list_admins(zawiya_id=payload.zawiya_id)