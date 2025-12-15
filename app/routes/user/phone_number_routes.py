# ============================================================
# PHONE NUMBER ROUTES
# ============================================================

from beanie import PydanticObjectId
from fastapi import APIRouter

from app.core.utils.dependencies import RegularUser
from app.crud import user_phone_number_crud
from app.schemas.user.phone_number_schema import PhoneNumberCreate, PhoneNumberUpdate

phone_router = APIRouter(prefix="/phone-numbers", tags=["Phone Numbers"])


@phone_router.post("/")
async def create(phone_data: PhoneNumberCreate, current_user: RegularUser):
    return await user_phone_number_crud.add(phone_data, current_user)


@phone_router.get("/me")
async def my(current_user: RegularUser):
    return await user_phone_number_crud.my_list(current_user)


@phone_router.get("/{phone_id}")
async def get_one(phone_id: PydanticObjectId, current_user: RegularUser):
    return await user_phone_number_crud.my_get(phone_id, current_user)


@phone_router.patch("/{phone_id}")
async def update(phone_id: PydanticObjectId, phone_data: PhoneNumberUpdate,
                 current_user: RegularUser):
    return await user_phone_number_crud.my_update(
        phone_id,
        phone_data.model_dump(exclude_unset=True),
        current_user
    )


@phone_router.post("/{phone_id}/verify")
async def verify(phone_id: PydanticObjectId, current_user: RegularUser):
    return await user_phone_number_crud.my_verify(phone_id, current_user)


@phone_router.post("/{phone_id}/set-primary")
async def set_primary(phone_id: PydanticObjectId, current_user: RegularUser):
    return await user_phone_number_crud.my_set_primary(phone_id, current_user)


@phone_router.delete("/{phone_id}")
async def delete(phone_id: PydanticObjectId, current_user: RegularUser):
    await user_phone_number_crud.my_delete(phone_id, current_user)
    return None
