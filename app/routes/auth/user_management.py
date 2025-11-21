from fastapi import APIRouter, Body
import logging
from app.schemas.user_schema import UserCreate, UserLogin, VerificationCode
from app.core.auth_service.auth_utils import get_verification, verify_email
from app.core.auth_service.user_auth import user_create_service, user_login_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/create/", response_model=dict)
async def user_create(user_data: UserCreate = Body(...)):
    return await user_create_service(user_data)

@router.post("/login")
async def login_user(user_data: UserLogin = Body(...)):
    return await user_login_service(user_data)

@router.post("/get/verification-code/")
async def get_code(user_data: VerificationCode):
    """
    Generate a verification code and log/send it to the user's email.
    """
    return await get_verification(user_data.email)

@router.post("/verify/email/")
async def verify_user_email(user_data: VerificationCode):
    """
    Verify the user's email using the provided verification code.
    """
    return await verify_email(user_data.email, user_data.verification_code)