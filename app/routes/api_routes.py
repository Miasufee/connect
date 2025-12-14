from fastapi import APIRouter
from app.routes.auth.user_auth_routes import router as user_management_router
from app.routes.auth.google_oauth_rotes import router as google_oauth_router
from app.routes.auth.admin_auth_routes import router as admin_auth_router
from app.routes.auth.logout_routes import router as logout_router
from app.routes.auth.password_reset_routes import router as password_reset_router
from app.routes.auth.role_management_routes import router as role_management_router
from app.routes.zawiya.zawiya_admin_routes import router as zawiya_admin_router
from app.routes.zawiya.zawiya_address_routes import router as address_router
from app.routes.zawiya.zawiya_profile_routes import router as zawiya_profile_router
from app.routes.zawiya.zawiya_subscription_routes import router as zawiya_subscription_router
from app.routes.user.superuser_routes import router as superuser_router
from .auth.refreshd_routes import refresh_router
from .auth.verification_code_routes import verification_router
from .user.user_profile_routes import profile_router
from .user.phone_number_routes import phone_router
from .user.user_prefrences import preferences_router
from .zawiya.zawiya_toutes import zawiya_router

api_router = APIRouter()

api_router.include_router(user_management_router, tags=["User Management"])
api_router.include_router(google_oauth_router, tags=["Google OAuth"])
api_router.include_router(admin_auth_router, tags=["Admin Auth"])
api_router.include_router(logout_router, tags=["Logout"])
api_router.include_router(password_reset_router, tags=["Password Reset"])
api_router.include_router(role_management_router, tags=["Role Management"])
api_router.include_router(zawiya_router)
api_router.include_router(zawiya_admin_router, tags=["admin-management"])
api_router.include_router(address_router, tags=["address routes"])
api_router.include_router(zawiya_profile_router, tags=["zawiya profile router"])
api_router.include_router(zawiya_subscription_router, tags=["zawiya subscription "])
api_router.include_router(superuser_router, tags=["superuser routes"])
api_router.include_router(profile_router)
api_router.include_router(phone_router)
api_router.include_router(preferences_router)
api_router.include_router(refresh_router)
api_router.include_router(verification_router)