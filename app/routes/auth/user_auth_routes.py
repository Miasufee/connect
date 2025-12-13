from fastapi import APIRouter, Body
import logging
from app.schemas.user.user_auth_schema import UserCreate, UserLogin
from app.services.user.user_service import user_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/create/", response_model=dict)
async def _user_create(user_data: UserCreate = Body(...)):
    return await user_service.create_user(user_data)

@router.post("/login")
async def _login_user(user_data: UserLogin = Body(...)):
    return await user_service.login_user(user_data)