from datetime import datetime, timezone
from typing import Optional, List, Union
from pydantic import EmailStr
from beanie import PydanticObjectId

from .crud_base import CrudBase
from ..models.user_models import User


class UserCRUD(CrudBase[User]):
    def __init__(self):
        super().__init__(User)

    async def get_user_by_id(self, user_id: Union[str, PydanticObjectId]) -> Optional[User]:
        """Get user by MongoDB _id."""
        return await self.get(user_id)

    async def get_by_email(self, email: EmailStr) -> Optional[User]:
        return await self.get_one(email=email)

    async def get_by_unique_id(self, unique_id: str) -> Optional[User]:
        return await self.get_one(unique_id=unique_id)

    async def deactivate_user(self, user_id: str) -> Optional[User]:
        return await self.update(user_id, {"is_active": False})

    async def activate_user(self, user_id: str) -> Optional[User]:
        return await self.update(user_id, {"is_active": True})

    async def get_active_users(self) -> List[User]:
        return await self.get_multi(is_active=True)

    async def get_users_by_role(self, user_role: str) -> List[User]:
        return await self.get_multi(user_role=user_role)

    async def verify_email(self, user_id: str) -> Optional[User]:
        return await self.update(user_id, {"is_email_verified": True})

    async def update_last_login(self, user_id: str):
        return await self.update(
            user_id,
            {"last_login_at": datetime.now(timezone.utc)}
        )

    async def increment_token_version(self, user_id: str) -> Optional[User]:
        user = await self.get(user_id)
        if user:
            user.token_version += 1
            await user.save()
            return user
        return None

    async def search_users(self, query: str, limit: int = 50) -> List[User]:
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

    async def get_list_of_user(self, page=1, per_page=20, **filters):
        return await self.paginate(
            page=page,
            per_page=per_page,
            filters=filters or {}
        )


user_crud = UserCRUD()
