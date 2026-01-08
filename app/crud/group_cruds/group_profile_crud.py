from beanie import PydanticObjectId

from app.crud import CrudBase
from app.models.group_models import GroupProfile


class GroupProfileCrud(CrudBase[GroupProfile]):
    """ GroupProfile Crud Management """
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

group_profile_crud = GroupProfileCrud()