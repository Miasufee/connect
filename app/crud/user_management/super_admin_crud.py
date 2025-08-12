from fastapi import Depends

from app.core.dependencies import get_current_superuser
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import CrudBase
from app.models.enums import UserRole
from app.models.user.user import User


class SuperAdminCrud(CrudBase[User]):
    def __init__(self):
        super().__init__(User)

    async def promote_to_admin(
        self,
        db: AsyncSession,
        user_id: int,
        current_user: User = Depends(get_current_superuser)
    ):
        """Superuser promotes a user to ADMIN"""
        return await self.update(db, obj_id=user_id, role=UserRole.ADMIN)

    async def verify_admin(
        self,
        db: AsyncSession,
        user_id: int,
        current_user: User = Depends(get_current_superuser)
    ):
        """Superuser verifies an admin"""
        return await self.update(db, obj_id=user_id, is_email_verified=True)

super_admin_crud = SuperAdminCrud()
