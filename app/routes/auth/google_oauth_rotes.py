from fastapi import APIRouter, Request
from app.core.auth_service.google_oauth import google_oauth

router = APIRouter()

@router.get("/google/login")
async def google_login_browser(request: Request):
    return await google_oauth.login_browser(request)

@router.post("/api/google/login")
async def google_login_api(request: Request):
    return await google_oauth.login_api(request)