from beanie import PydanticObjectId

from app.crud import CrudBase
from app.models.zawiya_models import ZawiyaAddress

class ZawiyaAddressCrud(CrudBase[ZawiyaAddress]):
    def __init__(self):
        super().__init__(ZawiyaAddress)

    async def set_address(
        self,
        zawiya_id: PydanticObjectId,
        country: str,
        state: str,
        city: str,
        address: str,
        postal_code: str,
        latitude: float,
        longitude: float
    ):
        existing = await self.get_one(zawiya_id=zawiya_id)
        data = {
            "country": country,
            "state": state,
            "city": city,
            "address": address,
            "postal_code": postal_code,
            "latitude": latitude,
            "longtitude": longitude
        }

        if existing:
            return await self.update(existing.id, data)

        return await self.create(zawiya_id=zawiya_id, **data)

    async def get_address(self, zawiya_id: PydanticObjectId):
        return await self.get_one(zawiya_id=zawiya_id)
