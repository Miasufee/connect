from __future__ import annotations

from beanie import PydanticObjectId
from fastapi import APIRouter, status, Query

from app.core.dependencies import RegularUser, AdminSuperAdmin
from app.core.response.exceptions import Exceptions
from app.schemas.zawiya.zawiya import ZawiyaCreate, ZawiyaVerify
from app.services.zawiya.zawiya_service import zawiya_service

zawiya_router = APIRouter(prefix="/zawiya", tags=["Zawiya"])


# ---------------- CREATE ----------------
@zawiya_router.post("/create/", status_code=status.HTTP_201_CREATED)
async def _create_zawiya(payload: ZawiyaCreate, owner: RegularUser = None):
    return await zawiya_service.create(
        title=payload.title,
        name=payload.name,
        description=payload.description,
        owner_id=owner.id,
    )


# ---------------- VERIFY ----------------
@zawiya_router.post("/verify/", status_code=status.HTTP_201_CREATED)
async def _verify_zawiya(payload: ZawiyaVerify, admin: AdminSuperAdmin = None):
    return await zawiya_service.verify(
        zawiya_id=payload.zawiya_id,
        verified_by=admin.id,
    )


# ---------------- LIST (PAGINATED) ----------------
@zawiya_router.get("/", status_code=status.HTTP_200_OK)
async def list_zawiya(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, le=100),
    is_verified: bool | None = None,
):
    return await zawiya_service.list(
        page=page,
        per_page=per_page,
        is_verified=is_verified,
    )


# ---------------- UPDATE ----------------
@zawiya_router.patch("/{zawiya_id}")
async def update_zawiya(
    zawiya_id: str,
    data: dict,
    user: RegularUser = None,
):
    return await zawiya_service.update(
        zawiya_id=zawiya_id,
        data=data,
        user_id=user.id,
    )


# ---------------- SOFT DELETE ----------------
@zawiya_router.delete("/{zawiya_id}")
async def delete_zawiya(zawiya_id: str, user: RegularUser = None):
    return await zawiya_service.soft_delete(
        zawiya_id=zawiya_id,
        user_id=user.id,
    )

# ---------------- GET BY QUERY ----------------

@zawiya_router.get("/get/", status_code=status.HTTP_200_OK)
async def get_zawiya(
    zawiya_id: str | None = Query(None),
    title: str | None = Query(None),
    name: str | None = Query(None),
):
    """
    Get zawiya by:
    - id
    - title
    - name
    """
    # Clean input
    if zawiya_id:
        zawiya_id = zawiya_id.strip().replace('"', '')
        try:
            zawiya_id_obj = PydanticObjectId(zawiya_id)
        except Exception:
            raise Exceptions.bad_request("Invalid zawiya_id")
    else:
        zawiya_id_obj = None

    return await zawiya_service.get(
        zawiya_id=zawiya_id_obj,
        title=title,
        name=name,
    )


# ---------------- SMART SEARCH ----------------

@zawiya_router.get("/search")
async def search_zawiya(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    is_verified: bool | None = None,
):
    return await zawiya_service.search(
        query=q,
        page=page,
        per_page=per_page,
        is_verified=is_verified,
    )
