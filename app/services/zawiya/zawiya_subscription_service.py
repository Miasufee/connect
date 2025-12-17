from beanie import PydanticObjectId


from app.core.response.exceptions import Exceptions
from app.crud.zawiya_cruds import zawiya_subscription_crud
from app.models.zawiya_models import NotificationLevel


class ZawiyaSubscriptionService:
    """Service layer for Zawiya subscriptions."""

    async def subscribe_user(
        self,
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
        level: NotificationLevel = NotificationLevel.PERSONALIZED
    ):
        """
        Subscribe a user to a Zawiya with a specific notification level.
        Upserts to prevent duplicate subscriptions.
        """
        return await zawiya_subscription_crud.subscribe(
            user_id=user_id,
            zawiya_id=zawiya_id,
            level=level
        )

    async def unsubscribe_user(self, user_id: PydanticObjectId, zawiya_id: PydanticObjectId):
        """
        Remove a user's subscription.
        """
        sub = await zawiya_subscription_crud.is_subscribed(user_id, zawiya_id)
        if not sub:
            raise Exceptions.not_found("Subscription does not exist")
        return await zawiya_subscription_crud.unsubscribe(user_id, zawiya_id)

    async def change_notification_level(
        self,
        user_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
        level: NotificationLevel
    ):
        """
        Update the notification level for an existing subscription.
        """
        return await zawiya_subscription_crud.update_level(user_id, zawiya_id, level)

    async def check_subscription(self, user_id: PydanticObjectId, zawiya_id: PydanticObjectId):
        """
        Check if a user is subscribed to a Zawiya.
        Returns the subscription object if exists, else None.
        """
        return await zawiya_subscription_crud.is_subscribed(user_id, zawiya_id)

    async def count_subscribers(self, zawiya_id: PydanticObjectId) -> int:
        """
        Get total subscribers for a specific Zawiya.
        """
        return await zawiya_subscription_crud.total_subscribers(zawiya_id)


# Singleton instance for use in routes
zawiya_subscription_service = ZawiyaSubscriptionService()
