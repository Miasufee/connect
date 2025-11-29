from beanie import PydanticObjectId

from app.crud import CrudBase
from app.models.zawiya_models import ZawiyaProfile

class ZawiyaProfileCrud(CrudBase[ZawiyaProfile]):
    def __init__(self):
        super().__init__(ZawiyaProfile)

    async def create_or_update_profile(
        self,
        zawiya_id: PydanticObjectId,
        avatar: str | None = None,
        banner: str | None = None,
        sheik: str | None = None
    ):
        existing = await self.get_one(zawiya_id=zawiya_id)
        data = {
            "zawiya_avatar": avatar,
            "zawiya_banner": banner,
            "zawiya_sheik": sheik
        }

        if existing:
            return await self.update(existing.id, data)

        return await self.create(
            zawiya_id=zawiya_id,
            **data
        )

    async def get_profile(self, zawiya_id: PydanticObjectId):
        return await self.get_one(zawiya_id=zawiya_id)

    async def delete_zawiya_profile(self, zawiya_id: PydanticObjectId):
        return await self.delete_by_filter(zawiya_id=zawiya_id)

zawiya_profile_crud = ZawiyaProfileCrud()