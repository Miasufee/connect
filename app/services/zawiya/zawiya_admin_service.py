from __future__ import annotations

from typing import List
from beanie import PydanticObjectId

from app.core.response.exceptions import Exceptions
from app.models.zawiya_models import ZawiyaAdmin, ZawiyaRoles
from app.crud.zawiya_cruds.zawiya_admin_crud import zawiya_admin_crud


class ZawiyaAdminService:

    # ---------------- ADD ADMIN ----------------
    async def add_admin(
        self,
        *,
        owner_id: PydanticObjectId,
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
        role: ZawiyaRoles,
    ) -> ZawiyaAdmin:
        try:
            return await zawiya_admin_crud.add_admin(
                owner_id=owner_id,
                user_id=user_id,
                zawiya_id=zawiya_id,
                role=role,
            )
        except PermissionError:
            raise Exceptions.permission_denied(
                "Only the zawiya owner can add admins"
            )
        except ValueError as e:
            raise Exceptions.bad_request(str(e))

    # ---------------- UPDATE ROLE ----------------
    async def update_role(
        self,
        *,
        owner_id: PydanticObjectId,
        admin_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
        role: ZawiyaRoles,
    ) -> ZawiyaAdmin:
        try:
            return await zawiya_admin_crud.update_role(
                owner_id=owner_id,
                admin_id=admin_id,
                zawiya_id=zawiya_id,
                role=role,
            )
        except PermissionError:
            raise Exceptions.permission_denied(
                "Only the zawiya owner can update admin roles"
            )
        except ValueError as e:
            raise Exceptions.not_found(str(e))

    # ---------------- REMOVE ADMIN (SOFT DELETE) ----------------
    async def remove_admin(
        self,
        *,
        owner_id: PydanticObjectId,
        admin_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
    ) -> dict:
        try:
            await zawiya_admin_crud.remove_admin(
                owner_id=owner_id,
                admin_id=admin_id,
                zawiya_id=zawiya_id,
            )
            return {"removed": True}
        except PermissionError:
            raise Exceptions.permission_denied(
                "Only the zawiya owner can remove admins"
            )
        except ValueError as e:
            raise Exceptions.not_found(str(e))

    # ---------------- LIST ADMINS ----------------
    @staticmethod
    async def list_admin(
        zawiya_id: PydanticObjectId,
    ) -> List[ZawiyaAdmin]:
        return await zawiya_admin_crud.list_admins(zawiya_id)


zawiya_admin_service = ZawiyaAdminService()
