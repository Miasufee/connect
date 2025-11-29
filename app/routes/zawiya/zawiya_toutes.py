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
        owner_id=owner_id
    )

@router.post("/verify/",status_code=status.HTTP_201_CREATED)
async def _verify_zawiya(payload: ZawiyaVerify, verified_by: AdminSuperAdmin = None):
    """ Verify zawiya """
    return await zawiya_crud.verify_zawiya(
        zawiya_id=payload.zawiya_id,
        verified_by=verified_by
    )