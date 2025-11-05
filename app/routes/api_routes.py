from fastapi import APIRouter
from .auth_routes import user as user_router
from .auth_routes import utiils as utils_router

api_router = APIRouter()

api_router.include_router(user_router.router, prefix="/user", tags=["user"])
api_router.include_router(utils_router.router, prefix="/auth", tags=["auth utils"])