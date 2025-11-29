from beanie import PydanticObjectId
from pydantic import BaseModel

from app.models.zawiya_models import NotificationLevel


class ZawiyaSubscription(BaseModel):
    user_id: PydanticObjectId
    zawiya_id: PydanticObjectId

class ZawiyaSubscriptionNotificationLevel(ZawiyaSubscription):
    notification_level: NotificationLevel