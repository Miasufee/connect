from fastapi import APIRouter

from app.schemas.user.user_auth_schema import VerificationCode
from app.services.user.verification_service import verification_service

verification_router = APIRouter(tags=["verification-code"])

@verification_router.post("/get/verification-code/")
async def get_code(user_data: VerificationCode):
    """
    Generate a verification code and log/send it to the user's email.
    """
    return await verification_service.generate_verification_code(user_data.email)

@verification_router.post("/verify/email/")
async def verify_user_email(user_data: VerificationCode):
    """
    Verify the user's email using the provided verification code.
    """
    return await verification_service.verify_email(user_data.email, user_data.verification_code)