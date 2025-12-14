from fastapi import APIRouter
from app.schemas.user.user_auth_schema import RoleUpdate
from app.core.dependencies import ElevatedUser
from app.services.user.role_service import role_service

router = APIRouter()

@router.post("/toggle/user/")
async def update_user_roles(payload: RoleUpdate, actor: ElevatedUser):
    """
    Update user roles - accessible to both SuperUser and SuperAdmin
    """
    return await role_service.update_role(actor, payload.email, payload.new_role)