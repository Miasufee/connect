
from fastapi import APIRouter, HTTPException, status, Query

from app.core.utils.dependencies import RegularUser
from app.crud import user_profile_crud, user_phone_number_crud



# ============================================================
# ADMIN ROUTES (Optional)
# ============================================================

admin_router = APIRouter(prefix="/admin", tags=["Admin - User Management"])


@admin_router.get("/profiles", response_model=PaginatedResponse)
async def list_all_profiles(
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
        current_user: RegularUser = None
):
    """List all user profiles (admin only)"""
    if current_user.user_role not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    result = await user_profile_crud.paginate(page=page, per_page=per_page)
    return result


@admin_router.get("/phone-numbers", response_model=PaginatedResponse)
async def list_all_phone_numbers(
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
        verified_only: bool = Query(False),
        current_user: RegularUser = None
):
    """List all phone numbers (admin only)"""
    if current_user.user_role not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    filters = {"is_verified": True} if verified_only else {}
    result = await user_phone_number_crud.paginate(
        page=page,
        per_page=per_page,
        filters=filters
    )
    return result