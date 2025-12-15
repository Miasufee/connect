from fastapi import APIRouter
from app.core.utils.dependencies import CurrentUser
from app.core.utils.token_manager import token_manager
from app.core.response.success import Success

router = APIRouter()

@router.post("/logout/current")
async def logout_current(_: CurrentUser, refresh_token: str):
    """
    Logs out from the current device using the provided refresh token.
    """
    revoked = await token_manager.logout_current_device(refresh_token)
    if revoked:
        return Success.ok("Logged out from current device")
    return Success.ok("Token already invalid or expired")

@router.post("/logout/others")
async def logout_other_devices(current_user: CurrentUser, refresh_token: str):
    """
    Logs out from all devices except the current one.
    """
    revoked_count = await token_manager.logout_all_other_devices(current_user, refresh_token)
    return Success.ok(f"Logged out from {revoked_count} other device(s)")

@router.post("/logout/all")
async def logout_all_devices(current_user: CurrentUser):
    """
    Logs out from all devices for the current user.
    """
    revoked_count = await token_manager.logout_all_devices(str(current_user.id))
    return Success.ok(f"Logged out from {revoked_count} device(s)")