from __future__ import annotations
from typing import Annotated, TypeAlias, Iterable, Optional
from fastapi import Request, Depends

from app.models.user_models import User, UserRole
from app.core.security import security_manager
from app.core.response.exceptions import Exceptions

# -------------------------------
# Base Helper
# -------------------------------

async def _require_role(
    request: Request,
    allowed_roles: Optional[Iterable[UserRole]] = None
) -> User:
    """
    Fetch the currently authenticated user from the request and validate roles.

    Args:
        request (Request): The incoming FastAPI request object.
        allowed_roles (Optional[Iterable[UserRole]]): Roles that are allowed to access this endpoint.
            If None, any authenticated user is allowed.

    Raises:
        Exceptions.permission_denied: If the user is not authenticated or does not have an allowed role.

    Returns:
        User: The authenticated user object.
    """
    user = await security_manager.get_current_user(request)

    if allowed_roles is not None and user.user_role not in allowed_roles:
        raise Exceptions.permission_denied()

    return user


# -------------------------------
# Concrete Role Dependencies
# -------------------------------

async def _current_user(request: Request) -> User:
    """
    Dependency for any authenticated user.

    Args:
        request (Request): FastAPI request object.

    Returns:
        User: The authenticated user.
    """
    return await _require_role(request)


async def _admin_user(request: Request) -> User:
    """
    Dependency for Admin and higher-level users (Admin, Super Admin, Super User).

    Args:
        request (Request): FastAPI request object.

    Returns:
        User: The authenticated user.

    Raises:
        Exceptions.permission_denied: If user role is not allowed.
    """
    return await _require_role(
        request,
        allowed_roles=[UserRole.admin, UserRole.super_admin, UserRole.superuser],
    )


async def _super_admin_user(request: Request) -> User:
    """
    Dependency for Super Admin only.

    Args:
        request (Request): FastAPI request object.

    Returns:
        User: The authenticated Super Admin.

    Raises:
        Exceptions.permission_denied: If user is not Super Admin.
    """
    return await _require_role(request, allowed_roles=[UserRole.super_admin])


async def _super_user(request: Request) -> User:
    """
    Dependency for Super User only.

    Args:
        request (Request): FastAPI request object.

    Returns:
        User: The authenticated Super User.

    Raises:
        Exceptions.permission_denied: If user is not Super User.
    """
    return await _require_role(request, allowed_roles=[UserRole.superuser])


async def _admin_super_admin(request: Request) -> User:
    """
    Dependency for Admin or Super Admin roles.

    Args:
        request (Request): FastAPI request object.

    Returns:
        User: Authenticated user with Admin or Super Admin role.

    Raises:
        Exceptions.permission_denied: If user role is not Admin or Super Admin.
    """
    return await _require_role(request, allowed_roles=[UserRole.admin, UserRole.super_admin])


async def _super_user_super_admin(request: Request) -> User:
    """
    Dependency for Super User or Super Admin roles.

    Args:
        request (Request): FastAPI request object.

    Returns:
        User: Authenticated user with Super User or Super Admin role.

    Raises:
        Exceptions.permission_denied: If user role is not Super User or Super Admin.
    """
    return await _require_role(
        request, allowed_roles=[UserRole.superuser, UserRole.super_admin]
    )


# -------------------------------
# FastAPI Annotated Aliases
# -------------------------------

CurrentUser: TypeAlias = Annotated[User, Depends(_current_user)]
RegularUser: TypeAlias = Annotated[User, Depends(_current_user)]

AdminUser: TypeAlias = Annotated[User, Depends(_admin_user)]
SuperAdminUser: TypeAlias = Annotated[User, Depends(_super_admin_user)]
SuperUser: TypeAlias = Annotated[User, Depends(_super_user)]

AdminSuperAdmin: TypeAlias = Annotated[User, Depends(_admin_super_admin)]
ElevatedUser: TypeAlias = Annotated[User, Depends(_super_user_super_admin)]
