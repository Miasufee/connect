from beanie import PydanticObjectId

from app.crud import CrudBase
from app.models.zawiya_models import ZawiyaSubscription, NotificationLevel

class ZawiyaSubscriptionCrud(CrudBase[ZawiyaSubscription]):
    def __init__(self):
        super().__init__(ZawiyaSubscription)

    async def subscribe(
        self,
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
        level: NotificationLevel = NotificationLevel.PERSONALIZED
    ):
        existing = await self.get_one(user_id=user_id, zawiya_id=zawiya_id)
        if existing:
            existing.notification_level = level
            return await existing.save()

        return await self.create(
            user_id=user_id,
            zawiya_id=zawiya_id,
            notification_level=level
        )

    async def unsubscribe(self, user_id: PydanticObjectId, zawiya_id: PydanticObjectId):
        return await self.delete_by_filter(user_id=user_id, zawiya_id=zawiya_id)

    async def update_level(
        self,
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
        level: NotificationLevel
    ):
        sub = await self.get_one(user_id=user_id, zawiya_id=zawiya_id)
        if not sub:
            raise ValueError("User is not subscribed")

        sub.notification_level = level
        return await sub.save()

    async def is_subscribed(self, user_id: PydanticObjectId, zawiya_id: PydanticObjectId):
        return await self.get_one(user_id=user_id, zawiya_id=zawiya_id)
