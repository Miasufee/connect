# app/crud/user_phone_number_crud.py

from fastapi import HTTPException, status
from datetime import datetime

from ..crud_base import CrudBase
from ...models import PhoneNumber


class UserPhoneNumberCrud(CrudBase[PhoneNumber]):
    def __init__(self):
        super().__init__(PhoneNumber)

    # --------------------------------------------------
    # Add phone
    # --------------------------------------------------
    async def add(self, phone_data, current_user):
        if str(current_user.id) != str(phone_data.user_id):
            raise HTTPException(status_code=403)

        exists = await self.get_one(
            user_id=phone_data.user_id,
            phone_number=phone_data.phone_number
        )
        if exists:
            raise HTTPException(status_code=400)

        if phone_data.is_primary:
            user_phones = await self.get_multi(
                filters={"user_id": phone_data.user_id, "is_primary": True}
            )
            for phone in user_phones:
                await self.update(phone.id, {"is_primary": False})

        return await self.create(**phone_data.model_dump())

    # --------------------------------------------------
    # all phones for me
    # --------------------------------------------------
    async def my_list(self, current_user):
        return await self.get_multi(
            filters={"user_id": current_user.id},
            order_by=[("is_primary", -1), ("created_at", -1)]
        )

    # --------------------------------------------------
    # get single (and ensure owner)
    # --------------------------------------------------
    async def my_get(self, phone_id, current_user):
        phone = await self.get(phone_id)
        if not phone:
            raise HTTPException(status_code=404)

        if str(phone.user_id) != str(current_user.id):
            raise HTTPException(status_code=403)

        return phone

    # --------------------------------------------------
    # update (and enforce primary)
    # --------------------------------------------------
    async def my_update(self, phone_id, update_data, current_user):
        phone = await self.my_get(phone_id, current_user)

        if update_data.get("is_primary"):
            user_phones = await self.get_multi(
                filters={"user_id": phone.user_id, "is_primary": True}
            )
            for p in user_phones:
                if str(p.id) != str(phone_id):
                    await self.update(p.id, {"is_primary": False})

        return await self.update(phone_id, update_data)

    # --------------------------------------------------
    # verify
    # --------------------------------------------------
    async def my_verify(self, phone_id, current_user):
        phone = await self.my_get(phone_id, current_user)

        if phone.is_verified:
            raise HTTPException(status_code=400)

        return await self.update(
            phone_id,
            {"is_verified": True, "verified_at": datetime.utcnow()}
        )

    # --------------------------------------------------
    # set primary
    # --------------------------------------------------
    async def my_set_primary(self, phone_id, current_user):
        return await self.my_update(phone_id, {"is_primary": True}, current_user)

    # --------------------------------------------------
    # delete
    # --------------------------------------------------
    async def my_delete(self, phone_id, current_user):
        await self.my_get(phone_id, current_user)
        await self.delete(phone_id)


user_phone_number_crud = UserPhoneNumberCrud()