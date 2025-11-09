# app/crud/user_crud.py
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import EmailStr
from .crud_base import CrudBase
from ..models.user_models import User


class UserCRUD(CrudBase[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, email: EmailStr) -> Optional[User]:
        """Get user by email address."""
        return await self.get_one(email=email)

    async def get_by_unique_id(self, unique_id: str) -> Optional[User]:
        """Get user by unique_id."""
        return await self.get_one(unique_id=unique_id)

    async def deactivate_user(self, user_id: str) -> Optional[User]:
        """Deactivate a user."""
        return await self.update(user_id, {"is_active": False})

    async def activate_user(self, user_id: str) -> Optional[User]:
        """Activate a user."""
        return await self.update(user_id, {"is_active": True})

    async def get_active_users(self) -> List[User]:
        """Get all active users."""
        return await self.get_multi(is_active=True)

    async def get_users_by_role(self, role: str) -> List[User]:
        """Get users by role."""
        return await self.get_multi(role=role)

    async def verify_email(self, user_id: str) -> Optional[User]:
        """Mark user's email as verified."""
        return await self.update(user_id, {"is_email_verified": True})

    async def update_last_login(self, user_id: str):
        """Update user's last login timestamp."""
        return await self.update(
            user_id,
            {"last_login_at": datetime.now(timezone.utc)}
        )

    async def increment_token_version(self, user_id: str) -> Optional[User]:
        """Increment token version (useful for logout all devices)."""
        user = await self.get(user_id)
        if user:
            user.token_version += 1
            await user.save()
            return user
        return None

    async def update_profile(self, user_id: str, profile_data: dict) -> Optional[User]:
        """Update user profile."""
        return await self.update(user_id, {"profile": profile_data})

    async def add_phone_number(self, user_id: str, phone_data: dict) -> Optional[User]:
        """Add a phone number to user."""
        user = await self.get(user_id)
        if user:
            user.phone_numbers.append(phone_data)
            await user.save()
            return user
        return None

    async def add_social_account(self, user_id: str, social_data: dict) -> Optional[User]:
        """Add a social account to user."""
        user = await self.get(user_id)
        if user:
            user.social_accounts.append(social_data)
            await user.save()
            return user
        return None

    async def search_users(self, query: str, limit: int = 50) -> List[User]:
        """Search users by email or profile names."""
        return await self.get_multi(
            filters={
                "$or": [
                    {"email": {"$regex": query, "$options": "i"}},
                    {"profile.first_name": {"$regex": query, "$options": "i"}},
                    {"profile.last_name": {"$regex": query, "$options": "i"}},
                ]
            },
            limit=limit
        )


# Global instance
user_crud = UserCRUD()