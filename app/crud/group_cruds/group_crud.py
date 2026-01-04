from typing import Optional

from beanie import PydanticObjectId

from app.crud import CrudBase
from app.crud.group_cruds.group_member_crud import group_member_crud
from app.models import VisibilityStatus
from app.models.group_models import Group


class GroupCrud(CrudBase[Group]):
    def __init__(self):
        super().__init__(Group)

    async def create_group(
            self,
            zawiya_id: PydanticObjectId,
            user_id: PydanticObjectId,
            title: str,
            description: str | None,
            created_by: PydanticObjectId
    ):
        group = await self.create(
            zawiya_id=zawiya_id,
            user_id=user_id,
            title=title,
            description=description,
            created_by=created_by
        )
        await group_member_crud.create_group_owner(
            group_id=group.id,
            created_by=group.created_by
        )
        return group

    async def get_group(self, group_id: PydanticObjectId):
        return await self.get(group_id)

    async def get_zawiya_groups(self, zawiya_id: PydanticObjectId):
        return await self.paginate(zawiya_id=zawiya_id)

    async def list_public_groups(
        self,
        page: int = 1,
        per_page: int = 20,
    ):
        return await self.paginate(
            page=page,
            per_page=per_page,
            visibility=VisibilityStatus.PUBLIC,
            is_deleted=False,
        )

    async def list_groups(
        self,
        zawiya_id: Optional[PydanticObjectId] = None,
        visibility: Optional[VisibilityStatus] = None,
        page: int = 1,
        per_page: int = 20,
    ):
        return await self.paginate(
            page=page,
            per_page=per_page,
            zawiya_id=zawiya_id,
            visibility=visibility,
            is_deleted=False,
        )


    async def update_group(
        self,
        group_id: PydanticObjectId,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Group]:
        return await self.update(
            group_id,
            {
                "title": title,
                "description": description,
            },
        )

    async def update_visibility(
        self,
        group_id: PydanticObjectId,
        visibility: VisibilityStatus,
    ) -> Optional[Group]:
        return await self.update(group_id, {"visibility": visibility})

    async def delete_group(self, group_id: PydanticObjectId) -> bool:
        return await self.soft_delete(group_id)

    async def restore_group(self, group_id: PydanticObjectId) -> bool:
        return await self.restore(group_id)


    async def count_groups(
        self,
        zawiya_id: Optional[PydanticObjectId] = None,
        visibility: Optional[VisibilityStatus] = None,
    ) -> int:
        return await self.count(
            zawiya_id=zawiya_id,
            visibility=visibility,
            is_deleted=False,
        )




group_crud = GroupCrud()