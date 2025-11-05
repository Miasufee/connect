from fastapi import APIRouter
from app.core.auth_service.auth_utils import get_verification, verify_email
from app.schemas.user_schema import VerificationCode

router = APIRouter()


@router.post("/get/verification-code/")
async def get_code(user_data: VerificationCode):
    """
    Generate a verification code and log/send it to the user’s email.
    """
    return await get_verification(user_data.email)


@router.post("/verify/email/")
async def verify_user_email(user_data: VerificationCode):
    """
    Verify the user's email using the provided verification code.
    """
    return await verify_email(user_data.email, user_data.verification_code)
