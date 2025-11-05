from fastapi import  Request

from typing import Annotated, TypeAlias
from fastapi import Depends
from app.models.user_models import User
from app.core.security import security_manager
from app.core.response.exceptions import Exceptions

# ---- Dependency functions ----
async def _current_user(request: Request) -> User:
    return await security_manager.get_current_user(request)

async def _admin_user(request: Request) -> User:
    user = await security_manager.get_current_user(request)
    if user.role not in ["admin", "super_admin"]:
        raise Exceptions.permission_denied()
    return user

async def _super_admin_user(request: Request) -> User:
    user = await security_manager.get_current_user(request)
    if user.role != "super_admin":
        raise Exceptions.permission_denied()
    return user

async def _super_user(request: Request) -> User:
    user = await security_manager.get_current_user(request)
    if user.role not in ["super_user", "super_admin"]:
        raise Exceptions.permission_denied()
    return user

# ---- Annotated aliases ----
CurrentUser: TypeAlias = Annotated[User, Depends(_current_user)]
RegularUser: TypeAlias = Annotated[User, Depends(_current_user)]
MerchantUser: TypeAlias = Annotated[User, Depends(_current_user)]
AdminUser: TypeAlias = Annotated[User, Depends(_admin_user)]
SuperAdminUser: TypeAlias = Annotated[User, Depends(_super_admin_user)]
SuperUser: TypeAlias = Annotated[User, Depends(_super_user)]
