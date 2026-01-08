from fastapi import HTTPException, status

from ..crud_base import CrudBase
from ...models import UserProfile


class UserProfileCrud(CrudBase[UserProfile]):
    """ User Profile Crud Management """
    def __init__(self):
        super().__init__(UserProfile)

    # ---------------------
    # Create Profile
    # ---------------------
    async def create_profile(self, profile_data):
        existing = await self.get_one(user_id=profile_data.user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile already exists"
            )
        return await self.create(**profile_data.model_dump())

    # ---------------------
    # Get current profile
    # ---------------------
    async def get_my_profile(self, current_user):
        profile = await self.get_one(user_id=current_user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        return profile

    # ---------------------
    # Update current profile
    # ---------------------
    async def update_my_profile(self, update_data, current_user):
        profile = await self.get_one(user_id=current_user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Create first"
            )

        return await self.update(profile.id, update_data)


    # ---------------------
    # Delete
    # ---------------------
    async def delete_my_profile(self, current_user):
        profile = await self.get_one(user_id=current_user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found"
            )

        await self.delete(profile.id)
        return True

user_profile_crud = UserProfileCrud()