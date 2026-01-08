from fastapi import HTTPException

from app.crud import CrudBase
from app.models import UserPreferences


class UserPreferencesCrud(CrudBase[UserPreferences]):
    """ User Preferences Crud Management """
    def __init__(self):
        super().__init__(UserPreferences)

    # ---------------------------------------------
    # create only if none & enforce self access
    # ---------------------------------------------
    async def my_create(self, data, current_user):
        if str(current_user.id) != str(data.user_id):
            raise HTTPException(status_code=403)

        existing = await self.get_one(user_id=data.user_id)
        if existing:
            raise HTTPException(status_code=400)

        return await self.create(**data.model_dump())

    # ---------------------------------------------
    # get, auto-create if missing
    # ---------------------------------------------
    async def my_get(self, current_user):
        preferences = await self.get_one(user_id=current_user.id)
        if preferences:
            return preferences

        return await self.create(user_id=current_user.id)

    # ---------------------------------------------
    # update only self
    # ---------------------------------------------
    async def my_update(self, data, current_user):
        preferences = await self.get_one(user_id=current_user.id)
        if not preferences:
            raise HTTPException(status_code=404)

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return preferences

        return await self.update(preferences.id, update_data)

    # ---------------------------------------------
    # delete (reset to default)
    # ---------------------------------------------
    async def my_delete(self, current_user):
        preferences = await self.get_one(user_id=current_user.id)
        if not preferences:
            raise HTTPException(status_code=404)

        await self.delete(preferences.id)


user_preferences_crud = UserPreferencesCrud()