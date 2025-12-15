from __future__ import annotations

from beanie import PydanticObjectId

from app.core.response.exceptions import Exceptions
from app.core.response.success import Success
from app.crud.zawiya_cruds import zawiya_address_crud
from app.services.zawiya.zawiya_permissions import zawiya_permission


class ZawiyaAddressService:

    @staticmethod
    async def create_or_update_address(
            zawiya_id: PydanticObjectId,
            user_id: PydanticObjectId,
            country: str | None = None,
            state: str | None = None,
            city: str | None = None,
            address: str | None = None,
            postal_code: str | None = None,
            latitude: float | None = None,
            longitude: float | None = None
    ):
        await zawiya_permission.require_admin_or_owner(
            zawiya_id=zawiya_id,
            user_id=user_id
        )

        return await zawiya_address_crud.set_address(
            zawiya_id=zawiya_id,
            country=country,
            state=state,
            city=city,
            address=address,
            postal_code=postal_code,
            latitude=latitude,
            longitude=longitude
        )

    @staticmethod
    async def get_zawiya_address(
            zawiya_id: PydanticObjectId
    ):
        address = await zawiya_address_crud.get_address(zawiya_id=zawiya_id)
        if not address:
            Exceptions.not_found(detail="Address not found")
        return address

    @staticmethod
    async def delete_address(
            zawiya_id: PydanticObjectId,
            user_id: PydanticObjectId
    ):
        await zawiya_permission.require_owner(zawiya_id=zawiya_id, user_id=user_id)

        deleted = await zawiya_address_crud.delete_zawiya_address(zawiya_id=zawiya_id)
        if not deleted:
            raise Exceptions.not_found("zawiya address not found")
        return Success.content_deleted()

zawiya_address_service = ZawiyaAddressService()
