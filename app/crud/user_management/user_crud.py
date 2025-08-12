from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from app.crud.base import CrudBase
from app.models.user.user import User
from app.models.enums import UserRole
from app.schemas.user_schema import UserUpdate, UserResponse, PaginatedResponse


class UserCrud(CrudBase[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.get(db, email=email)

    async def get_by_unique_id(self, db: AsyncSession, unique_id: str) -> Optional[User]:
        """Get user by unique_id"""
        return await self.get(db, unique_id=unique_id)

    async def get_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """ get user by id"""
        return await self.get(db, id=user_id)

    async def update_password(self, db: AsyncSession, user_id: int, hashed_password: str) -> User:
        """Update user password"""
        return await self.update(db, obj_id=user_id, hashed_password=hashed_password)

    async def verify_email(self, db: AsyncSession, user_id: int) -> User:
        """Mark user email as verified"""
        return await self.update(db, obj_id=user_id, is_email_verified=True)

    async def approve_user(self, db: AsyncSession, user_id: int) -> User:
        """Approve user by admin"""
        return await self.update(db, obj_id=user_id, admin_approval=True)

    async def update_role(self, db: AsyncSession, user_id: int, role: UserRole) -> User:
        """Update user role"""
        return await self.update(db, obj_id=user_id, role=role)

    async def update_user_with_schema(
        self,
        db: AsyncSession,
        user_id: int,
        user_update: UserUpdate
    ) -> UserResponse:
        """Update user using schema"""
        update_data = user_update.model_dump(exclude_unset=True)
        user = await self.update(db, obj_id=user_id, **update_data)
        return UserResponse.model_validate(user)

    async def get_users_by_role(self, db: AsyncSession, role: UserRole, skip: int = 0, limit: int = 100) -> Sequence[
        User]:
        """Get users by role"""
        return await self.get_multi(db, skip=skip, limit=limit, role=role)

    async def get_unverified_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """Get unverified users"""
        return await self.get_multi(db, skip=skip, limit=limit, is_email_verified=False)

    async def get_pending_approval_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """Get users pending admin approval"""
        return await self.get_multi(db, skip=skip, limit=limit, admin_approval=False)

    async def search_users(self, db: AsyncSession, search_term: str, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """Search users by email or unique_id"""
        where_clause = or_(
            User.email.ilike(f"%{search_term}%"),
            User.unique_id.ilike(f"%{search_term}%")
        )
        return await self.get_multi(db, skip=skip, limit=limit, where_clause=where_clause)

    async def get_user_with_profile(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user with profile relationship loaded"""
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        
        async def _op():
            stmt = select(User).options(selectinload(User.profile)).where(User.id.is_(user_id))
            result = await db.execute(stmt)
            return result.scalars().first()
        
        return await self._execute_read_operation(db, "get_user_with_profile", _op)

    async def get_users_paginated(
        self,
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        **filters
    ) -> PaginatedResponse[UserResponse]:
        """Get paginated users with schema response"""
        result = await self.paginate(db, page=page, per_page=per_page, **filters)
        
        return PaginatedResponse[UserResponse](
            items=[UserResponse.model_validate(user) for user in result["items"]],
            total=result["total"],
            page=result["page"],
            per_page=result["per_page"],
            total_pages=result["total_pages"],
            has_next=result["has_next"],
            has_prev=result["has_prev"]
        )


user_crud = UserCrud()
