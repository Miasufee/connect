from beanie import PydanticObjectId
from app.core.response.exceptions import Exceptions
from app.crud.zawiya_cruds.zawiya_admin_crud import zawiya_admin_crud


class ZawiyaPermissionService:

    async def require_owner(self, *, zawiya_id: PydanticObjectId, user_id: PydanticObjectId):
        if not await zawiya_admin_crud.is_owner(user_id, zawiya_id):
            raise Exceptions.forbidden("Owner only")

    async def require_admin_or_owner(
        self, *, zawiya_id: PydanticObjectId, user_id: PydanticObjectId
    ):
        if await zawiya_admin_crud.is_owner(user_id, zawiya_id):
            return

        if not await zawiya_admin_crud.is_admin(user_id, zawiya_id):
            raise Exceptions.forbidden("Admin or Owner required")


zawiya_permission = ZawiyaPermissionService()
