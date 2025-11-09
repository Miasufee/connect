from app.core.auth_service.auth_utils import get_verification, verify_email
from app.schemas.user_schema import VerificationCode
from fastapi import APIRouter
from app.core.token_manager import token_manager
from app.core.dependencies import CurrentUser
from app.core.response.success import Success

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
