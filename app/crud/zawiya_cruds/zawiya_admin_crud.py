from typing import Optional, List
from beanie import PydanticObjectId

from app.models.zawiya_models import (
    Zawiya,
    ZawiyaAdmin,
    ZawiyaRoles
)


class ZawiyaAdminCRUD:

    # -----------------------------------------
    # Check if user is owner of the zawiya
    # -----------------------------------------
    @staticmethod
    async def is_owner(user_id: PydanticObjectId, zawiya_id: PydanticObjectId) -> bool:
        return await Zawiya.find_one(
            Zawiya.id == zawiya_id,
            Zawiya.owner_id == user_id,
            Zawiya.is_deleted == False
        ) is not None

    # -----------------------------------------
    # Check if user is already an admin
    # -----------------------------------------
    @staticmethod
    async def get_admin(
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId
    ) -> Optional[ZawiyaAdmin]:
        return await ZawiyaAdmin.find_one(
            ZawiyaAdmin.user_id == user_id,
            ZawiyaAdmin.zawiya_id == zawiya_id,
            ZawiyaAdmin.is_deleted == False
        )

    # -----------------------------------------
    # Add admin (owner only)
    # -----------------------------------------
    @staticmethod
    async def add_admin(
        owner_id: PydanticObjectId,
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
        role: ZawiyaRoles = ZawiyaRoles.Admin
    ) -> ZawiyaAdmin:

        # Only owners can add admins
        if not await ZawiyaAdminCRUD.is_owner(owner_id, zawiya_id):
            raise PermissionError("Only zawiya owner can add admins")

        # Prevent duplicates
        existing = await ZawiyaAdminCRUD.get_admin(user_id, zawiya_id)
        if existing:
            raise ValueError("User is already an admin for this zawiya")

        admin = ZawiyaAdmin(
            user_id=user_id,
            zawiya_id=zawiya_id,
            role=role
        )

        await admin.insert()
        return admin

    # -----------------------------------------
    # Remove admin (owner only)
    # -----------------------------------------
    @staticmethod
    async def remove_admin(
        owner_id: PydanticObjectId,
        admin_id: PydanticObjectId,
        zawiya_id: PydanticObjectId
    ) -> bool:

        # Only owner can remove local admins
        if not await ZawiyaAdminCRUD.is_owner(owner_id, zawiya_id):
            raise PermissionError("Only zawiya owner can remove admins")

        admin = await ZawiyaAdmin.get(admin_id)
        if not admin or admin.is_deleted:
            raise ValueError("Admin record not found")

        # Soft delete operation
        await admin.soft_delete()
        return True

    # -----------------------------------------
    # Update admin role (owner only)
    # -----------------------------------------
    @staticmethod
    async def update_role(
        owner_id: PydanticObjectId,
        admin_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
        new_role: ZawiyaRoles
    ) -> ZawiyaAdmin:

        if not await ZawiyaAdminCRUD.is_owner(owner_id, zawiya_id):
            raise PermissionError("Only zawiya owner can update admin roles")

        admin = await ZawiyaAdmin.get(admin_id)
        if not admin or admin.is_deleted:
            raise ValueError("Admin not found")

        admin.role = new_role
        await admin.save()

        return admin

    # -----------------------------------------
    # Get admins for a zawiya
    # -----------------------------------------
    @staticmethod
    async def list_zawiya_admins(
        zawiya_id: PydanticObjectId
    ) -> List[ZawiyaAdmin]:

        admins = await ZawiyaAdmin.find(
            ZawiyaAdmin.zawiya_id == zawiya_id,
            ZawiyaAdmin.is_deleted == False
        ).to_list()

        return admins

    # -----------------------------------------
    # Check if user is SuperAdmin of a zawiya
    # -----------------------------------------
    @staticmethod
    async def is_super_admin(
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId
    ) -> bool:

        admin = await ZawiyaAdmin.find_one(
            ZawiyaAdmin.user_id == user_id,
            ZawiyaAdmin.zawiya_id == zawiya_id,
            ZawiyaAdmin.role == ZawiyaRoles.SuperAdmin,
            ZawiyaAdmin.is_deleted == False
        )

        return admin is not None

    # -----------------------------------------
    # Check if user is local admin at all
    # -----------------------------------------
    @staticmethod
    async def is_local_admin(
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId
    ) -> bool:

        admin = await ZawiyaAdmin.find_one(
            ZawiyaAdmin.user_id == user_id,
            ZawiyaAdmin.zawiya_id == zawiya_id,
            ZawiyaAdmin.is_deleted == False
        )

        return admin is not None
