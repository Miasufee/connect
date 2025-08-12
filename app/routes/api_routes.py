from fastapi import APIRouter
from app.routes.user_management import users, phone_numbers, user_auth, addresses, auth_utils, superuser_auth

api_router = APIRouter()

api_router.include_router(user_auth.router, prefix="/user/auth", tags=["authentication"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(phone_numbers.router, prefix="/phone-numbers", tags=["phone-numbers"])
# api_router.include_router(addresses.router, prefix="/addresses", tags=["addresses"])
api_router.include_router(auth_utils.router, prefix="/auth/utils", tags=["authentication"])
api_router.include_router(superuser_auth.router, prefix="/superuser/auth")