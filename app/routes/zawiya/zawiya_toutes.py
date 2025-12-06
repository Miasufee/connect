from fastapi import APIRouter, status

from app.core.dependencies import RegularUser, AdminSuperAdmin
from app.crud.zawiya_cruds import zawiya_crud
from app.schemas.zawiya.zawiya import ZawiyaCreate, ZawiyaVerify

router = APIRouter(prefix="/zawiya")

@router.post("/create/", status_code=status.HTTP_201_CREATED)
async def _create_zawiya(payload: ZawiyaCreate, owner_id: RegularUser = None):
    """ Create zawiya """
    return await zawiya_crud.create_zawiya(
        title=payload.title,
        name=payload.name,
        description=payload.description,
        owner_id=owner_id.id
    )

@router.post("/verify/",status_code=status.HTTP_201_CREATED)
async def _verify_zawiya(payload: ZawiyaVerify, verified_by: AdminSuperAdmin = None):
    """ Verify zawiya """
    return await zawiya_crud.verify_zawiya(
        zawiya_id=payload.zawiya_id,
        verified_by=verified_by.id
    )

@router.get("/get/zawiya/lists/", status_code=status.HTTP_200_OK)
async def _list_of_zawiya():
    return await zawiya_crud.get_multi()

@router.get("/get/verified/zawiya/", status_code=status.HTTP_200_OK)
async def _lists_of_verified_zawiya():
    return await zawiya_crud.get_multi(filters={"is_verified": True})

@router.get("/get/unverified/zawiya/", status_code=status.HTTP_200_OK)
async def _lists_of_unverified_zawiya():
    return await zawiya_crud.get_multi(filters={"is_verified": False})