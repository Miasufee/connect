from fastapi import Request, Depends
from typing import Annotated, TypeAlias
from app.models.user_models import User, UserRole
from app.core.security import security_manager
from app.core.response.exceptions import Exceptions

# ---- Dependency functions ----
async def _current_user(request: Request) -> User:
    return await security_manager.get_current_user(request)

async def _admin_user(request: Request) -> User:
    """Admin, Super Admin, and Super User can access"""
    user = await security_manager.get_current_user(request)
    if user.user_role not in [UserRole.admin, UserRole.super_admin, UserRole.superuser]:
        raise Exceptions.permission_denied()
    return user

async def _super_admin_user(request: Request) -> User:
    """Only Super Admin can access"""
    user = await security_manager.get_current_user(request)
    if user.user_role != UserRole.super_admin:
        raise Exceptions.permission_denied()
    return user

async def _super_user(request: Request) -> User:
    """Only Super User can access"""
    user = await security_manager.get_current_user(request)
    if user.user_role != UserRole.superuser:
        raise Exceptions.permission_denied()
    return user

async def _elevated_user(request: Request) -> User:
    """Super User or Super Admin can access (for role management)"""
    user = await security_manager.get_current_user(request)
    if user.user_role not in [UserRole.superuser, UserRole.super_admin]:
        raise Exceptions.permission_denied()
    return user

# ---- Annotated aliases ----
CurrentUser: TypeAlias = Annotated[User, Depends(_current_user)]
RegularUser: TypeAlias = Annotated[User, Depends(_current_user)]
AdminUser: TypeAlias = Annotated[User, Depends(_admin_user)]
SuperAdminUser: TypeAlias = Annotated[User, Depends(_super_admin_user)]
SuperUser: TypeAlias = Annotated[User, Depends(_super_user)]
ElevatedUser: TypeAlias = Annotated[User, Depends(_elevated_user)]  # Better name