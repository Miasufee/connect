
from fastapi import APIRouter

from app.core.dependencies import RegularUser
from app.crud import user_preferences_crud
from app.schemas.user.user_preferences_schema import (
    UserPreferencesCreate,
    UserPreferencesUpdate,
    UserPreferencesResponse,
)


# ============================================================
# USER PREFERENCES ROUTES
# ============================================================

preferences_router = APIRouter(prefix="/preferences", tags=["User Preferences"])


@preferences_router.post("/", response_model=UserPreferencesResponse)
async def create(data: UserPreferencesCreate, current_user: RegularUser):
    return await user_preferences_crud.my_create(data, current_user)


@preferences_router.get("/me", response_model=UserPreferencesResponse)
async def get_me(current_user: RegularUser):
    return await user_preferences_crud.my_get(current_user)


@preferences_router.patch("/me", response_model=UserPreferencesResponse)
async def update_me(data: UserPreferencesUpdate, current_user: RegularUser):
    return await user_preferences_crud.my_update(data, current_user)


@preferences_router.delete("/me")
async def delete_me(current_user: RegularUser):
    await user_preferences_crud.my_delete(current_user)
    return None
