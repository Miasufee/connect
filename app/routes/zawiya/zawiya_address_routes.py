from fastapi import  APIRouter

from app.core.dependencies import RegularUser
from app.core.response.exceptions import Exceptions
from app.crud.zawiya_cruds import zawiya_address_crud
from app.crud.zawiya_cruds.zawiya_admin_crud import zawiya_admin_crud
from app.schemas.zawiya.zawiya_address import ZawiyaAddress, ZawiyaAddressCreate

router = APIRouter(prefix="/zawiya-address")

@router.post("/create/update")
async def create_or_update_address(payload: ZawiyaAddressCreate, owner: RegularUser = None):
    verify_owner = await zawiya_admin_crud.is_owner(
        user_id=owner.id,
        zawiya_id=payload.zawiya_id
    )
    if not verify_owner:
        raise Exceptions.permission_denied(detail="your not the owner")
    return await zawiya_address_crud.set_address(
        zawiya_id=payload.zawiya_id,
        country=payload.country,
        state=payload.state,
        city=payload.city,
        address=payload.address,
        postal_code=payload.postal_code,
        latitude=payload.latitude,
        longitude=payload.longitude
    )

@router.get("/get")
async def _get_zawiya_address(payload: ZawiyaAddress):
    return await zawiya_address_crud.get_address(
        zawiya_id=payload.zawiya_id
    )