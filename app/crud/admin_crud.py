from beanie import PydanticObjectId
from ..models.zawiya_models import ZawiyaAdmin, ZawiyaRole
from .crud_base import CrudBase


class ZawiyaAdminCrud(CrudBase[ZawiyaAdmin]):
    def __init__(self):
        super().__init__(ZawiyaAdmin)

    async def add_admin(
        self,
        zawiya_id: PydanticObjectId,
        user_id: PydanticObjectId,
        role: ZawiyaRole,
        acting_user_role: ZawiyaRole
    ):
        # Permission check
        if acting_user_role not in [ZawiyaRole.OWNER, ZawiyaRole.ADMIN]:
            raise PermissionError("Only Owner or Admin can add admins")

        if role == ZawiyaRole.OWNER:
            raise PermissionError("You cannot assign Owner role")

        existing = await self.get_one(zawiya_id=zawiya_id, user_id=user_id)
        if existing:
            raise ValueError("User is already an admin")

        return await self.create(
            zawiya_id=zawiya_id,
            user_id=user_id,
            role=role
        )

    async def change_role(
        self,
        zawiya_id: PydanticObjectId,
        user_id: PydanticObjectId,
        new_role: ZawiyaRole,
        acting_user_role: ZawiyaRole
    ):
        if acting_user_role != ZawiyaRole.OWNER:
            raise PermissionError("Only Owner can change admin roles")

        if new_role == ZawiyaRole.OWNER:
            raise PermissionError("You cannot assign Owner role")

        admin = await self.get_one(zawiya_id=zawiya_id, user_id=user_id)
        if not admin:
            raise ValueError("Admin not found")

        admin.role = new_role
        return await admin.save()

    async def remove_admin(
        self,
        zawiya_id: PydanticObjectId,
        user_id: PydanticObjectId,
        acting_user_role: ZawiyaRole
    ):
        if acting_user_role != ZawiyaRole.OWNER:
            raise PermissionError("Only Owner can remove admins")

        admin = await self.get_one(zawiya_id=zawiya_id, user_id=user_id)
        if not admin:
            raise ValueError("Admin not found")

        await admin.soft_delete()
        return True

    async def list_admins(self, zawiya_id: PydanticObjectId):
        return await self.get_multi(zawiya_id=zawiya_id)
