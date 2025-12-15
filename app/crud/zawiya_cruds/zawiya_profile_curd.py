from __future__ import annotations

from typing import Optional

from beanie import PydanticObjectId

from app.core.response.success import Success
from app.crud import CrudBase
from app.models.zawiya_models import ZawiyaProfile

class ZawiyaProfileCrud(CrudBase[ZawiyaProfile]):
    def __init__(self):
        super().__init__(ZawiyaProfile)

    async def create_or_update_profile(
            self,
            zawiya_id: PydanticObjectId | str,
            avatar: Optional[str] = None,
            banner: Optional[str] = None,
            sheik_name: Optional[str] = None,
    ):
        if isinstance(zawiya_id, str):
            zawiya_id = PydanticObjectId(zawiya_id)

        update_data = {
            "avatar": avatar,
            "banner": banner,
            "sheik_name": sheik_name,
        }

        # Remove None values (don’t overwrite existing fields)
        update_data = {k: v for k, v in update_data.items() if v is not None}

        await self.upsert(
            filters={"zawiya_id": zawiya_id},
            update_data=update_data,
        )
        return Success.created(message="profile created")

    async def get_profile(self, zawiya_id: PydanticObjectId):
        return await self.get_one(zawiya_id=zawiya_id)

    async def delete_zawiya_profile(self, zawiya_id: PydanticObjectId):
        return await self.delete_by_filter(zawiya_id=zawiya_id)

zawiya_profile_crud = ZawiyaProfileCrud()