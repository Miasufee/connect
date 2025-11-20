from beanie import PydanticObjectId

from app.crud import CrudBase
from app.models.zawiya_models import ZawiyaAnalytics

class ZawiyaAnalyticsCrud(CrudBase[ZawiyaAnalytics]):
    def __init__(self):
        super().__init__(ZawiyaAnalytics)

    async def get_or_create(self, zawiya_id: PydanticObjectId):
        existing = await self.get_one(zawiya_id=zawiya_id)
        if existing:
            return existing

        return await self.create(zawiya_id=zawiya_id)

    async def increment(
        self,
        zawiya_id: PydanticObjectId,
        field: str,
        amount: int = 1
    ):
        analytics = await self.get_or_create(zawiya_id)
        value = getattr(analytics, field)
        setattr(analytics, field, value + amount)
        return await analytics.save()

    # Example helpers
    async def add_video(self, zawiya_id: PydanticObjectId):
        return await self.increment(zawiya_id, "total_videos")

    async def add_like(self, zawiya_id: PydanticObjectId):
        return await self.increment(zawiya_id, "total_likes")

    async def add_subscriber(self, zawiya_id: PydanticObjectId):
        return await self.increment(zawiya_id, "total_subscribers")
