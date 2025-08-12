from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CrudBase
from app.models.user.user import UserProfile
from app.schemas.user_schema import UserProfileCreate, UserProfileUpdate, UserProfileResponse


class UserProfileCrud(CrudBase[UserProfile]):
    def __init__(self):
        super().__init__(UserProfile)

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> Optional[UserProfile]:
        """Get profile by user_id"""
        return await self.get(db, user_id=user_id)

    async def create_profile(
        self,
        db: AsyncSession,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> UserProfile:
        """Create user profile"""
        return await self.create(
            db,
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            avatar_url=avatar_url
        )

    async def create_profile_with_schema(
        self,
        db: AsyncSession,
        profile_create: UserProfileCreate
    ) -> UserProfileResponse:
        """Create profile using schema"""
        profile = await self.create(db, **profile_create.model_dump())
        return UserProfileResponse.model_validate(profile)

    async def update_profile(
        self,
        db: AsyncSession,
        user_id: int,
        **kwargs: Any
    ) -> UserProfile:
        """Update user profile"""
        profile = await self.get_by_user_id(db, user_id)
        if not profile:
            raise ValueError(f"Profile for user {user_id} not found")
        return await self.update(db, db_obj=profile, **kwargs)

    async def update_profile_with_schema(
        self,
        db: AsyncSession,
        user_id: int,
        profile_update: UserProfileUpdate
    ) -> UserProfileResponse:
        """Update profile using schema"""
        update_data = profile_update.model_dump(exclude_unset=True)
        profile = await self.update_profile(db, user_id, **update_data)
        return UserProfileResponse.model_validate(profile)

    async def update_avatar(self, db: AsyncSession, user_id: int, avatar_url: str) -> UserProfile:
        """Update user avatar"""
        return await self.update_profile(db, user_id, avatar_url=avatar_url)

    async def get_full_name(self, db: AsyncSession, user_id: int) -> Optional[str]:
        """Get user's full name"""
        profile = await self.get(db, user_id=user_id, columns=['first_name', 'last_name'])
        if profile and profile.first_name and profile.last_name:
            return f"{profile.first_name} {profile.last_name}"
        return None


user_profile_crud = UserProfileCrud()
