from typing import List, Optional

from beanie import PydanticObjectId

from app.core.response.exceptions import Exceptions
from app.crud.crud_base import CrudBase
from app.crud.zawiya_cruds import zawiya_crud
from app.models.zawiya_models import ZawiyaAdmin, ZawiyaRoles


class ZawiyaAdminCRUD(CrudBase[ZawiyaAdmin]):

    def __init__(self):
        super().__init__(ZawiyaAdmin)

    # =====================================================
    # OWNER CHECKS
    # =====================================================

    @staticmethod
    async def is_owner(
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
    ) -> bool:
        zawiya = await zawiya_crud.get_by_id(zawiya_id)
        return bool(
            zawiya
            and not zawiya.is_deleted
            and zawiya.owner_id == user_id
        )

    async def require_owner(
        self,
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
    ) -> None:
        if not await self.is_owner(user_id, zawiya_id):
            raise Exceptions.forbidden("Owner only")

    # =====================================================
    # ADMIN LOOKUPS
    # =====================================================

    async def get_admin(
        self,
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
    ) -> Optional[ZawiyaAdmin]:
        return await self.model.find_one(
            ZawiyaAdmin.user_id == user_id,
            ZawiyaAdmin.zawiya_id == zawiya_id,
            ZawiyaAdmin.is_deleted == False,
        )

    async def _get_admin_or_404(
        self,
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
    ) -> ZawiyaAdmin:
        admin = await self.model.find_one(
            ZawiyaAdmin.user_id == user_id,
            ZawiyaAdmin.zawiya_id == zawiya_id,
            ZawiyaAdmin.is_deleted == False,
        )
        if not admin:
            raise Exceptions.not_found("Admin not found")
        return admin

    async def is_admin(
        self,
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
    ) -> bool:
        return await self.get_admin(user_id, zawiya_id) is not None

    async def is_admin_or_owner(
        self,
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
    ) -> bool:
        if await self.is_owner(user_id, zawiya_id):
            return True
        return await self.is_admin(user_id, zawiya_id)

    # =====================================================
    # ADD ADMIN (WITH RESTORE SUPPORT)
    # =====================================================

    async def add_admin(
        self,
        *,
        owner_id: PydanticObjectId,
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
        role: ZawiyaRoles = ZawiyaRoles.ADMIN,
    ) -> ZawiyaAdmin:

        await self.require_owner(owner_id, zawiya_id)

        if owner_id == user_id:
            raise Exceptions.conflict("Owner cannot be added as admin")

        existing = await self.model.find_one(
            ZawiyaAdmin.user_id == user_id,
            ZawiyaAdmin.zawiya_id == zawiya_id,
        )

        # Restore soft-deleted admin
        if existing:
            if not existing.is_deleted:
                raise Exceptions.conflict("User is already an admin")

            existing.is_deleted = False
            existing.role = role
            await existing.save()
            return existing

        return await self.create(
            user_id=user_id,
            zawiya_id=zawiya_id,
            role=role,
        )

    # =====================================================
    # UPDATE ADMIN ROLE
    # =====================================================

    async def update_role(
        self,
        *,
        owner_id: PydanticObjectId,
        admin_user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
        role: ZawiyaRoles,
    ) -> ZawiyaAdmin:

        await self.require_owner(owner_id, zawiya_id)

        admin = await self._get_admin_or_404(admin_user_id, zawiya_id)

        if admin.user_id == owner_id:
            raise Exceptions.conflict("Owner role cannot be modified")

        if admin.role == role:
            raise Exceptions.conflict("Role is already assigned")

        admin.role = role
        await admin.save()
        return admin

    # =====================================================
    # REMOVE ADMIN (SOFT DELETE)
    # =====================================================

    async def remove_admin(
        self,
        *,
        owner_id: PydanticObjectId,
        admin_user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
    ) -> None:

        await self.require_owner(owner_id, zawiya_id)

        admin = await self._get_admin_or_404(admin_user_id, zawiya_id)

        if admin.user_id == owner_id:
            raise Exceptions.conflict("Owner cannot be removed")

        await admin.soft_delete()

    # =====================================================
    # LIST ADMINS
    # =====================================================

    async def list_admins(
        self,
        zawiya_id: PydanticObjectId,
    ) -> List[ZawiyaAdmin]:
        return await self.model.find(
            ZawiyaAdmin.zawiya_id == zawiya_id,
            ZawiyaAdmin.is_deleted == False,
        ).to_list()


zawiya_admin_crud = ZawiyaAdminCRUD()
