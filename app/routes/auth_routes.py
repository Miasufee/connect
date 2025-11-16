from fastapi import APIRouter, Request, Body
import logging

from app.core.auth_service.password_reset import password_reset_service
from app.schemas.user_schema import PasswordResetRequest, PasswordResetResponse, PasswordResetValidate, \
    PasswordResetConfirm
from app.core.auth_service.auth_utils import get_verification, verify_email, login_superuser_or_admins
from app.core.auth_service.google_oauth import google_oauth
from app.core.auth_service.user_auth import user_create_service, user_login_service
from app.core.dependencies import CurrentUser
from app.core.response.success import Success
from app.core.token_manager import token_manager
from app.schemas.user_schema import UserCreate, UserLogin, VerificationCode, SuperUserLogin

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/create/", response_model=dict)
async def user_create(user_data: UserCreate = Body(...)):
    return await user_create_service(user_data)


@router.post("/login")
async def login_user(user_data: UserLogin = Body(...)):
    return await user_login_service(user_data)


@router.get("/google/login")
async def google_login_browser(request: Request):
    return await google_oauth.login_browser(request)



@router.post("/api/google/login")
async def google_login_api(request: Request):
    return await google_oauth.login_api(request)


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


# -------------------------
# Logout Current Device
# -------------------------
@router.post("/logout/current")
async def logout_current(_: CurrentUser, refresh_token: str):
    """
    Logs out from the current device using the provided refresh token.
    """
    revoked = await token_manager.logout_current_device(refresh_token)
    if revoked:
        return Success.ok("Logged out from current device")
    return Success.ok("Token already invalid or expired")


# -------------------------
# Logout All Other Devices
# -------------------------
@router.post("logout/others")
async def logout_other_devices(current_user: CurrentUser, refresh_token: str):
    """
    Logs out from all devices except the current one.
    """
    revoked_count = await token_manager.logout_all_other_devices(current_user, refresh_token)
    return Success.ok(f"Logged out from {revoked_count} other device(s)")


# -------------------------
# Logout All Devices
# -------------------------
@router.post("logout/all")
async def logout_all_devices(current_user: CurrentUser):
    """
    Logs out from all devices for the current user.
    """
    revoked_count = await token_manager.logout_all_devices(str(current_user.id))
    return Success.ok(f"Logged out from {revoked_count} device(s)")

@router.post("/login/superuser/")
async def _login_superuser(payload: SuperUserLogin):
    return await login_superuser_or_admins(payload.email, payload.unique_id, payload.password)



@router.post("/password-reset/request", response_model=PasswordResetResponse)
async def request_password_reset(request: PasswordResetRequest):
    """
    Step 1: Request password reset - sends email with reset link.

    Frontend: User enters email → calls this endpoint → shows success message
    """

    return await password_reset_service.request_password_reset(request.email)



@router.post("/password-reset/validate-token", response_model=PasswordResetResponse)
async def validate_reset_token(request: PasswordResetValidate):
    """
    Step 2: Validate reset token when user clicks email link.

    Frontend: When user opens reset link → calls this to validate token → shows reset form if valid
    """

    return await password_reset_service.validate_reset_token(
            email=request.email,
            token=request.token
        )


@router.post("/password-reset/confirm", response_model=PasswordResetResponse)
async def confirm_password_reset(request: PasswordResetConfirm):
    """
    Step 3: Process password reset with new password.

    Frontend: User enters new password → calls this endpoint → shows success/error
    """
    return await password_reset_service.reset_password(
            email=request.email,
            token=request.token,
            new_password=request.new_password,
            confirm_password=request.confirm_password
        )
