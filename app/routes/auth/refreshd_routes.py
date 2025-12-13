from fastapi import APIRouter, Request
from app.services.user.refresh_service import RefreshService
from app.core.response.success import Success

refresh_router = APIRouter(tags=["Auth"])

@refresh_router.post("/auth/refresh")
async def refresh_token(request: Request):
    """
    Refresh access and refresh tokens using a valid refresh token.
    Sets new tokens as HTTP-only cookies and returns the response
    exactly like login_success.
    """
    # Get new tokens and the user from the refresh service
    access_token, new_refresh_token, user = await RefreshService.refresh_token_pair(request)

    # Return response mimicking login success
    return Success.login_success(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=user
    )

