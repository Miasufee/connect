from fastapi import APIRouter, Body

from app.schemas.user.user_auth_schema import SuperUserLogin, UserOut, LoginResponse
from app.services.user.admin_auth_service import admin_auth_service

router = APIRouter()

@router.post("/login/admins/", response_model=LoginResponse)
async def login_superuser_super_admin_admin(payload: SuperUserLogin = Body(...)):
    return await admin_auth_service.login(payload.email, payload.unique_id, payload.password)
