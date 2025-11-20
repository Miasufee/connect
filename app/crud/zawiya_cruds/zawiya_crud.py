from beanie import PydanticObjectId
from ..crud_base import CrudBase
from app.models.zawiya_models import Zawiya

class ZawiyaCrud(CrudBase[Zawiya]):
    def __init__(self):
        super().__init__(Zawiya)

    async def create_zawiya(
        self,
        title: str,
        name: str,
        description: str,
        owner_id: PydanticObjectId,
        created_by: PydanticObjectId
    ):
        # Validation
        if await self.get_one(title=title):
            raise ValueError("Title already exists")
        if await self.get_one(name=name):
            raise ValueError("Name already exists")

        return await self.create(
            title=title,
            name=name,
            description=description,
            owner_id=owner_id,
            created_by=created_by,
            is_verified=False
        )

    async def verify(self, zawiya_id: PydanticObjectId):
        return await self.update(zawiya_id, {"is_verified": True})

    async def update_zawiya(self, zawiya_id: PydanticObjectId, data: dict):
        return await self.update(zawiya_id, data)
