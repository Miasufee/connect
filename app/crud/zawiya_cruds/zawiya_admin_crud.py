from typing import Optional, List
from beanie import PydanticObjectId

from app.models.zawiya_models import Zawiya, ZawiyaAdmin, ZawiyaRoles
from app.crud.crud_base import CrudBase


class ZawiyaAdminCRUD(CrudBase[ZawiyaAdmin]):
    """
    CRUD for Zawiya Admins with:
    - Owner-only management rules
    - Role updates
    - Prevent duplicate admins
    """

    def __init__(self):
        super().__init__(ZawiyaAdmin)

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------
    @staticmethod
    async def is_owner(user_id: PydanticObjectId, zawiya_id: PydanticObjectId) -> bool:
        """Check if user owns the zawiya."""
        zawiya = await Zawiya.find_one(
            Zawiya.id == zawiya_id,
            Zawiya.owner_id == user_id,
            Zawiya.is_deleted == False
        )
        return zawiya is not None

    async def get_admin(
        self, user_id: PydanticObjectId, zawiya_id: PydanticObjectId
    ) -> Optional[ZawiyaAdmin]:
        """Get admin record for a user in a zawiya."""
        return await self.model.find_one(
            ZawiyaAdmin.user_id == user_id,
            ZawiyaAdmin.zawiya_id == zawiya_id,
            ZawiyaAdmin.is_deleted == False
        )

    async def is_super_admin(
        self, user_id: PydanticObjectId, zawiya_id: PydanticObjectId
    ) -> bool:
        """Check if user is SuperAdmin for zawiya."""
        admin = await self.model.find_one(
            ZawiyaAdmin.user_id == user_id,
            ZawiyaAdmin.zawiya_id == zawiya_id,
            ZawiyaAdmin.role == ZawiyaRoles.SuperAdmin,
            ZawiyaAdmin.is_deleted == False
        )
        return admin is not None

    async def is_local_admin(
        self, user_id: PydanticObjectId, zawiya_id: PydanticObjectId
    ) -> bool:
        """Check if user is any level of admin."""
        admin = await self.model.find_one(
            ZawiyaAdmin.user_id == user_id,
            ZawiyaAdmin.zawiya_id == zawiya_id,
            ZawiyaAdmin.is_deleted == False
        )
        return admin is not None

    # -----------------------------------------------------
    # Create admin
    # -----------------------------------------------------
    async def add_admin(
        self,
        owner_id: PydanticObjectId,
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
        role: ZawiyaRoles = ZawiyaRoles.Admin
    ) -> ZawiyaAdmin:
        """
        Add a new admin.
        Only Zawiya Owner can assign admins.
        Prevents duplicate admin assignment.
        """

        if not await self.is_owner(owner_id, zawiya_id):
            raise PermissionError("Only the Zawiya owner can add admins")

        # Check duplicates
        existing = await self.get_admin(user_id, zawiya_id)
        if existing:
            raise ValueError("User is already an admin of this Zawiya")

        return await self.create(
            user_id=user_id,
            zawiya_id=zawiya_id,
            role=role
        )

    # -----------------------------------------------------
    # Update role
    # -----------------------------------------------------
    async def update_role(
        self,
        owner_id: PydanticObjectId,
        admin_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
        new_role: ZawiyaRoles
    ) -> ZawiyaAdmin:

        if not await self.is_owner(owner_id, zawiya_id):
            raise PermissionError("Only the Zawiya owner can update admin roles")

        admin = await self.get(admin_id)
        if not admin or admin.is_deleted:
            raise ValueError("Admin not found")

        admin.role = new_role
        await admin.save()
        return admin

    # -----------------------------------------------------
    # Remove admin (Soft Delete)
    # -----------------------------------------------------
    async def remove_admin(
        self,
        owner_id: PydanticObjectId,
        admin_id: PydanticObjectId,
        zawiya_id: PydanticObjectId
    ) -> bool:

        if not await self.is_owner(owner_id, zawiya_id):
            raise PermissionError("Only the Zawiya owner can remove admins")

        admin = await self.get(admin_id)
        if not admin or admin.is_deleted:
            raise ValueError("Admin record not found")

        await admin.soft_delete()
        return True

    # -----------------------------------------------------
    # List admins
    # -----------------------------------------------------
    async def list_admins(self, zawiya_id: PydanticObjectId) -> List[ZawiyaAdmin]:
        """Return all active admins for a Zawiya."""
        return await self.model.find(
            ZawiyaAdmin.zawiya_id == zawiya_id,
            ZawiyaAdmin.is_deleted == False
        ).to_list()

zawiya_admin_crud = ZawiyaAdminCRUD()