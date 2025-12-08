from fastapi import APIRouter, Query
from typing import Optional
from app.crud import user_crud
from app.core.dependencies import SuperUser
from app.models import UserRole
from app.schemas.user.user_auth_schema import UserOut, PaginatedUsers

router = APIRouter()

@router.get("/get/users/",response_model=PaginatedUsers)
async def _get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    _: SuperUser = None
):
    """
    Get paginated users with optional filters:
    - user_role: filter by role
    - is_active: filter by active status
    """
    filters = {}
    if user_role is not None:
        filters["user_role"] = user_role
    if is_active is not None:
        filters["is_active"] = is_active

    return await user_crud.get_list_of_user(page=page, per_page=per_page, **filters)

@router.get("/get/super-admin/", response_model=PaginatedUsers)
async def _get_super_admin(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _: SuperUser = None
):
    return await user_crud.get_list_of_user(
        page=page,
        per_page=per_page,
        user_role=UserRole.super_admin.value
    )
