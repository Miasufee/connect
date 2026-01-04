from typing import Optional

from beanie import PydanticObjectId

from app.crud import CrudBase
from app.models.group_models import GroupProfile


class GroupProfileCrud(CrudBase[GroupProfile]):
    def __init__(self):
        super().__init__(GroupProfile)

    async def set_profile(
        self,
        group_id: PydanticObjectId,
        avatar_url: str,
    ) -> GroupProfile:
        existing = await self.get(group_id)
        if existing:
            await existing.set({"avatar_url": avatar_url})
            return existing

        return await self.create(
            group_id=group_id,
            avatar_url=avatar_url
        )

    async def get_Profile_profile(self, group_id: PydanticObjectId) -> Optional[GroupProfile]:
        return await self.get(group_id)

    async def delete_group_profile(self, group_id):
        return await self.delete(group_id)

group_profile_crud = GroupProfileCrud()