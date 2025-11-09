from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging

from app.core.auth_service.password_reset import password_reset_service
from app.core.response.exceptions import Exceptions

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class PasswordResetRequest(BaseModel):
    unique_id: str
    email: EmailStr


class PasswordResetValidate(BaseModel):
    email: EmailStr
    token: str


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class PasswordResetResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


@router.post("/password-reset/request", response_model=PasswordResetResponse)
async def request_password_reset(request: PasswordResetRequest):
    """
    Step 1: Request password reset - sends email with reset link.

    Frontend: User enters email → calls this endpoint → shows success message
    """
    try:
        result = await password_reset_service.request_password_reset(request.email)
        return PasswordResetResponse(
            success=True,
            message=result.get("message", "Reset email sent if account exists"),
            data=None
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in password reset request: {e}")
        raise Exceptions.internal_server_error()


@router.post("/password-reset/validate-token", response_model=PasswordResetResponse)
async def validate_reset_token(request: PasswordResetValidate):
    """
    Step 2: Validate reset token when user clicks email link.

    Frontend: When user opens reset link → calls this to validate token → shows reset form if valid
    """
    try:
        validation_result = await password_reset_service.validate_reset_token(
            email=request.email,
            token=request.token
        )

        return PasswordResetResponse(
            success=True,
            message=validation_result.get("message", "Token is valid"),
            data=validation_result
        )

    except HTTPException as e:
        return PasswordResetResponse(
            success=False,
            message=str(e.detail),
            data={"valid": False}
        )
    except Exception as e:
        logger.error(f"Unexpected error in token validation: {e}")
        raise Exceptions.internal_server_error()


@router.post("/password-reset/confirm", response_model=PasswordResetResponse)
async def confirm_password_reset(request: PasswordResetConfirm):
    """
    Step 3: Process password reset with new password.

    Frontend: User enters new password → calls this endpoint → shows success/error
    """
    try:
        result = await password_reset_service.reset_password(
            email=request.email,
            token=request.token,
            new_password=request.new_password,
            confirm_password=request.confirm_password
        )

        return PasswordResetResponse(
            success=True,
            message=result.get("message", "Password reset successfully"),
            data=None
        )

    except HTTPException as e:
        return PasswordResetResponse(
            success=False,
            message=str(e.detail),
            data=None
        )
    except Exception as e:
        logger.error(f"Unexpected error in password reset confirmation: {e}")
        raise Exceptions.internal_server_error()


@router.get("/password-requirements")
async def get_password_requirements():
    """
    Get password requirements for frontend validation.

    Frontend: Use these rules to validate password before submitting
    """
    return await password_reset_service.get_password_requirements()