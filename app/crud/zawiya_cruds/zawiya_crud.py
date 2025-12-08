from __future__ import annotations

from beanie import PydanticObjectId
from ..crud_base import CrudBase
from app.models.zawiya_models import Zawiya
from ...core.response.exceptions import Exceptions


class ZawiyaCrud(CrudBase[Zawiya]):
    def __init__(self):
        super().__init__(Zawiya)

    async def create_zawiya(
        self,
        title: str,
        name: str,
        description: str | None,
        owner_id: PydanticObjectId,
    ):
        # Validation
        if await self.get_one(title=title):
            raise Exceptions.forbidden(detail="Title already exists")
        if await self.get_one(name=name):
            raise Exceptions.forbidden(detail="Name already exists")

        return await self.create(
            title=title,
            name=name,
            description=description,
            owner_id=owner_id,
            is_verified=False
        )

    async def verify_zawiya(self, zawiya_id: PydanticObjectId, verified_by: PydanticObjectId):
        return await self.update(zawiya_id, {"is_verified": True, "verified_by": verified_by})

    async def update_zawiya(self, zawiya_id: PydanticObjectId, data: dict):
        return await self.update(zawiya_id, data)


zawiya_crud = ZawiyaCrud()