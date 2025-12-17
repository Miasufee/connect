from beanie import PydanticObjectId

from app.core.response.exceptions import Exceptions
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
        return await self.upsert(
            filters={
                "user_id": user_id,
                "zawiya_id": zawiya_id,
            },
            update_data={
                "notification_level": level
            }
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
            raise Exceptions.bad_request("User is not subscribed")

        sub.notification_level = level
        return await sub.save()

    async def is_subscribed(self, user_id: PydanticObjectId, zawiya_id: PydanticObjectId):
        return await self.get_one(user_id=user_id, zawiya_id=zawiya_id)

    async def total_subscribers(self, zawiya_id: PydanticObjectId):
        return await self.count(zawiya_id=zawiya_id)

zawiya_subscription_crud = ZawiyaSubscriptionCrud()