from fastapi import APIRouter
from app.routes.auth.user_management import router as user_management_router
from app.routes.auth.google_oauth import router as google_oauth_router
from app.routes.auth.admin_auth import router as admin_auth_router
from app.routes.auth.logout_router import router as logout_router
from app.routes.auth.password_reset import router as password_reset_router
from app.routes.auth.role_management import router as role_management_router

api_router = APIRouter()

api_router.include_router(user_management_router, tags=["User Management"])
api_router.include_router(google_oauth_router, tags=["Google OAuth"])
api_router.include_router(admin_auth_router, tags=["Admin Auth"])
api_router.include_router(logout_router, tags=["Logout"])
api_router.include_router(password_reset_router, tags=["Password Reset"])
api_router.include_router(role_management_router, tags=["Role Management"])