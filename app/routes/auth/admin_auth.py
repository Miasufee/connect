from fastapi import APIRouter, Body
from app.schemas.user_schema import SuperUserLogin
from app.core.auth_service.auth_utils import login_superuser_or_admins

router = APIRouter()

@router.post("/login/admins/")
async def login_superuser_super_admin_admin(payload: SuperUserLogin = Body(...)):
    return await login_superuser_or_admins(payload.email, payload.unique_id, payload.password)

@router.post("/login/superuser/")
async def login_superuser(payload: SuperUserLogin = Body(...)):
    return await login_superuser_or_admins(payload.email, payload.unique_id, payload.password)