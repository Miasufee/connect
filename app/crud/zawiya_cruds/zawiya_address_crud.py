from typing import Optional

from beanie import PydanticObjectId

from app.core.response.success import Success
from app.crud import CrudBase
from app.models.zawiya_models import ZawiyaAddress

class ZawiyaAddressCrud(CrudBase[ZawiyaAddress]):
    """ Zawiya Address Crud Management """
    def __init__(self):
        super().__init__(ZawiyaAddress)

    async def set_address(
        self,
        zawiya_id: PydanticObjectId,
        country: Optional[str] = None,
        state:  Optional[str] = None,
        city:  Optional[str] = None,
        address:  Optional[str] = None,
        postal_code:  Optional[str] = None,
        latitude:  Optional[float] = None,
        longitude:  Optional[float] = None
    ):
        if isinstance(zawiya_id, str):
            zawiya_id = PydanticObjectId(zawiya_id)

        data = {
            "country": country,
            "state": state,
            "city": city,
            "address": address,
            "postal_code": postal_code,
            "latitude": latitude,
            "longitude": longitude
        }

        update_data = {k: v for k, v in data.items() if v is not None}

        await self.upsert(
            filters={"zawiya_id": zawiya_id},
            update_data=update_data
        )

        return Success.ok(message="Address set successfully")

    async def get_address(self, zawiya_id: PydanticObjectId):
        return await self.get_one(zawiya_id=zawiya_id)

    async def delete_zawiya_address(self, zawiya_id: PydanticObjectId):
        return await self.delete_by_filter(zawiya_id=zawiya_id)

zawiya_address_crud = ZawiyaAddressCrud()
