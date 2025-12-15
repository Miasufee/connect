from fastapi import  APIRouter, status

from app.core.utils.dependencies import RegularUser
from app.schemas.zawiya.zawiya_address import ZawiyaAddress, ZawiyaAddressCreate
from app.services.zawiya.zawiya_address_service import zawiya_address_service

router = APIRouter(prefix="/zawiya-address")

@router.patch("/create/update", status_code=status.HTTP_201_CREATED)
async def _create_or_update_address(payload: ZawiyaAddressCreate, owner: RegularUser = None):

    return await zawiya_address_service.create_or_update_address(
        zawiya_id=payload.zawiya_id,
        user_id=owner.id,
        country=payload.country,
        state=payload.state,
        city=payload.city,
        address=payload.address,
        postal_code=payload.postal_code,
        latitude=payload.latitude,
        longitude=payload.longitude
    )

@router.get("/get", status_code=status.HTTP_200_OK)
async def _get_zawiya_address(payload: ZawiyaAddress):
    return await zawiya_address_service.get_zawiya_address(
        zawiya_id=payload.zawiya_id
    )

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def _delete_address(payload: ZawiyaAddress, owner: RegularUser = None):
    return await zawiya_address_service.delete_address(zawiya_id=payload.zawiya_id, user_id=owner.id)