from typing import List
from beanie import PydanticObjectId

from app.models.zawiya_models import ZawiyaAdmin, ZawiyaRoles
from app.crud.zawiya_cruds.zawiya_admin_crud import zawiya_admin_crud


class ZawiyaAdminService:

    # ---------------- ADD ADMIN ----------------
    @staticmethod
    async def add_admin(
        *,
        owner_id: PydanticObjectId,
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
        role: ZawiyaRoles,
    ) -> ZawiyaAdmin:

        return await zawiya_admin_crud.add_admin(
            owner_id=owner_id,
            user_id=user_id,
            zawiya_id=zawiya_id,
            role=role,
        )

    # ---------------- UPDATE ROLE ----------------
    @staticmethod
    async def update_role(
        self,
        *,
        owner_id: PydanticObjectId,
        admin_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
        role: ZawiyaRoles,
    ) -> ZawiyaAdmin:

        return await zawiya_admin_crud.update_role(
            owner_id=owner_id,
            admin_id=admin_id,
            zawiya_id=zawiya_id,
            role=role,
        )

    # ---------------- REMOVE ADMIN (SOFT DELETE) ----------------
    @staticmethod
    async def remove_admin(
        self,
        *,
        owner_id: PydanticObjectId,
        admin_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
    ) -> dict:

        await zawiya_admin_crud.remove_admin(
            owner_id=owner_id,
            admin_id=admin_id,
            zawiya_id=zawiya_id,
        )
        return {"removed": True}

    # ---------------- LIST ADMINS ----------------
    @staticmethod
    async def list_admin(
        zawiya_id: PydanticObjectId,
    ) -> List[ZawiyaAdmin]:
        return await zawiya_admin_crud.list_admins(zawiya_id)


zawiya_admin_service = ZawiyaAdminService()
