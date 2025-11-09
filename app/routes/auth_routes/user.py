
from fastapi import APIRouter, Body, status
from app.core.auth_service.user_auth import user_create_service, user_login_service
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse
from app.core.response.success import Success

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/create/", response_model=UserResponse)
async def user_create(user_data: UserCreate = Body(...)):
    """
    Create a regular user account and send a verification code.
    """
    return await user_create_service(user_data)


@router.post("/login")
async def login_user(user_data: UserLogin = Body(...)):
    """
    Log in user via email + verification code flow.
    """
    return await user_login_service(user_data)
