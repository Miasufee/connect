from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CrudBase
from app.models.user.user import SocialAccount
from app.models.enums import SocialProvider


class SocialAccountCrud(CrudBase[SocialAccount]):
    def __init__(self):
        super().__init__(SocialAccount)

    async def get_by_provider_and_user_id(
        self,
        db: AsyncSession,
        provider: SocialProvider,
        provider_user_id: str
    ) -> Optional[SocialAccount]:
        """Get social account by provider and provider user ID"""
        return await self.get(db, provider=provider, provider_user_id=provider_user_id)

    async def get_user_social_accounts(self, db: AsyncSession, user_id: int) -> Sequence[SocialAccount]:
        """Get all social accounts for a user"""
        return await self.get_multi(db, user_id=user_id)

    async def create_social_account(
        self,
        db: AsyncSession,
        user_id: int,
        provider: SocialProvider,
        provider_user_id: str,
        access_token: str
    ) -> SocialAccount:
        """Create a new social account"""
        return await self.create(
            db,
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            access_token=access_token
        )

    async def update_access_token(
        self,
        db: AsyncSession,
        account_id: int,
        access_token: str
    ) -> SocialAccount:
        """Update social account access token"""
        return await self.update(db, obj_id=account_id, access_token=access_token)

    async def get_by_provider(self, db: AsyncSession, provider: SocialProvider) -> Sequence[SocialAccount]:
        """Get all accounts for a specific provider"""
        return await self.get_multi(db, provider=provider)

    async def user_has_provider(
        self,
        db: AsyncSession,
        user_id: int,
        provider: SocialProvider
    ) -> bool:
        """Check if user has account with specific provider"""
        return await self.exists(db, user_id=user_id, provider=provider)

    async def delete_user_social_accounts(self, db: AsyncSession, user_id: int) -> None:
        """Delete all social accounts for a user"""
        await self.delete(db, user_id=user_id)


social_account_crud = SocialAccountCrud()
