from beanie import PydanticObjectId
from app.core.response.exceptions import Exceptions
from app.models.zawiya_models import ZawiyaAdmin, ZawiyaRoles


class ZawiyaPermissionService:
    """Zawiya role & ownership checks"""

    async def is_owner(self, zawiya_id: PydanticObjectId, user_id: PydanticObjectId) -> bool:
        return await ZawiyaAdmin.find_one(
            ZawiyaAdmin.zawiya_id == zawiya_id,
            ZawiyaAdmin.user_id == user_id,
            ZawiyaAdmin.role == ZawiyaRoles.SuperAdmin,
        ) is not None

    async def require_owner(self, zawiya, user_id):
        if zawiya.owner_id != user_id:
            raise Exceptions.forbidden("Only owner can perform this action")

    async def require_admin_or_owner(self, zawiya_id, user_id):
        admin = await ZawiyaAdmin.find_one(
            ZawiyaAdmin.zawiya_id == zawiya_id,
            ZawiyaAdmin.user_id == user_id,
        )
        if not admin:
            raise Exceptions.forbidden("Admin or Owner role required")


zawiya_permission = ZawiyaPermissionService()
