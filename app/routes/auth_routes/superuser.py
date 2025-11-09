from fastapi import APIRouter

from app.core.auth_service.auth_utils import login_superuser_or_admins
from app.schemas.user_schema import SuperUserLogin


router = APIRouter()

@router.post("/login/superuser/")
async def _login_superuser(payload: SuperUserLogin):
    return await login_superuser_or_admins(payload.email, payload.unique_id, payload.password)