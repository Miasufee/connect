"""
FastAPI routes for UserProfile
"""
from fastapi import APIRouter

from app.core.utils.dependencies import RegularUser
from app.crud import user_profile_crud
from app.schemas.user.user_profile_schema import (
    # Profile
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
)


# ============================================================
# USER PROFILE ROUTES
# ============================================================

profile_router = APIRouter(prefix="/profile", tags=["User Profile"])


@profile_router.post("/", response_model=UserProfileResponse)
async def create(profile_data: UserProfileCreate, _: RegularUser):
    return await user_profile_crud.create_profile(profile_data)


@profile_router.get("/me")
async def my(current_user: RegularUser):
    return await user_profile_crud.get_my_profile(current_user)


@profile_router.patch("/me")
async def update_me(profile_data: UserProfileUpdate, current_user: RegularUser):
    return await user_profile_crud.update_my_profile(
        profile_data.model_dump(exclude_unset=True),
        current_user
    )


@profile_router.delete("/me")
async def delete(current_user: RegularUser):
    await user_profile_crud.delete_my_profile(current_user)
    return None


