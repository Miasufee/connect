from fastapi import APIRouter, BackgroundTasks
from app.schemas.user.user_auth_schema import (
    PasswordResetRequest,
    PasswordResetResponse,
    PasswordResetValidate,
    PasswordResetConfirm
)
from app.core.auth_service.password_reset import password_reset_service

router = APIRouter()


@router.post("/password-reset/request", response_model=PasswordResetResponse)
async def request_password_reset(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks
):
    """
    Step 1: Request password reset - sends email with reset link.
    """
    return await password_reset_service.request_password_reset(
        email=request.email,
        unique_id=request.unique_id,
        background_tasks=background_tasks
    )


@router.post("/password-reset/validate-token")
async def _validate_reset_token(request: PasswordResetValidate):
    """
    Step 2: Validate reset token when user clicks email link.
    """
    return await password_reset_service.validate_reset_token(
        email=request.email,
        token=request.token
    )


@router.post("/password-reset/confirm")
async def confirm_password_reset(request: PasswordResetConfirm):
    """
    Step 3: Process password reset with new password.
    """
    return await password_reset_service.reset_password(
        email=request.email,
        token=request.token,
        new_password=request.new_password,
        confirm_password=request.confirm_password
    )
