from beanie import PydanticObjectId

from app.crud import CrudBase
from app.models.zawiya_models import ZawiyaAnalytics

class ZawiyaAnalyticsCrud(CrudBase[ZawiyaAnalytics]):
    """ Zawiya Analytics Crud Management """
    def __init__(self):
        super().__init__(ZawiyaAnalytics)

    async def get_or_create(self, zawiya_id: PydanticObjectId):
        return await self.upsert(
            filters={"zawiya_id": zawiya_id},
            update_data={}
        )

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

    async def add_livestream(self, zawiya_id: PydanticObjectId):
        return await self.increment(zawiya_id, "total_livestreams")

    async def add_content(self, zawiya_id: PydanticObjectId):
        return await self.increment(zawiya_id, "total_content")


zawiya_analytics_crud = ZawiyaAnalyticsCrud()