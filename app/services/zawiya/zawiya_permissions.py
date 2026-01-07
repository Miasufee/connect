from beanie import PydanticObjectId

from app.core.response.exceptions import Exceptions
from app.crud.zawiya_cruds.zawiya_admin_crud import zawiya_admin_crud


class ZawiyaPermissionService:
    """
    Central permission guard for Zawiya actions.
    """

    @staticmethod
    async def require_owner(
        *,
        zawiya_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ) -> None:
        if not await zawiya_admin_crud.is_owner(user_id, zawiya_id):
            raise Exceptions.forbidden("Owner only")

    @staticmethod
    async def require_admin_or_owner(
        *,
        zawiya_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ) -> None:
        if not await zawiya_admin_crud.is_admin_or_owner(user_id, zawiya_id):
            raise Exceptions.forbidden("Admin or Owner required")

    @staticmethod
    async def require_admin(
        *,
        zawiya_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ) -> None:
        if not await zawiya_admin_crud.is_admin(user_id, zawiya_id):
            raise Exceptions.forbidden("Admin only")


zawiya_permission = ZawiyaPermissionService()
