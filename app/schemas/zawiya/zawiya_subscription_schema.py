from __future__ import annotations

from beanie import PydanticObjectId
from pydantic import BaseModel

from app.models.zawiya_models import NotificationLevel


class ZawiyaSubscription(BaseModel):
    user_id: PydanticObjectId
    zawiya_id: PydanticObjectId

class ZawiyaSubscriptionNotificationLevel(ZawiyaSubscription):
    notification_level: NotificationLevel

class ZawiyaSubscriptionRequest(BaseModel):
    level: NotificationLevel = NotificationLevel.PERSONALIZED


class ZawiyaSubscriptionResponse(BaseModel):
    subscription_id: PydanticObjectId | None
    message: str
    success: bool
