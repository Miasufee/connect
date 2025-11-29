from fastapi import APIRouter

from app.crud.zawiya_cruds import zawiya_subscription_crud
from app.schemas.zawiya.zawiya_subscription import ZawiyaSubscription, ZawiyaSubscriptionNotificationLevel

router = APIRouter()

@router.post("/subscribe")
async def _subscribe(payload: ZawiyaSubscription):
    return await zawiya_subscription_crud.subscribe(
        user_id=payload.user_id,
        zawiya_id=payload.zawiya_id
    )

@router.delete("/unsubscribe")
async def _unsubscribe(payload: ZawiyaSubscription):
    return await zawiya_subscription_crud.unsubscribe(
        user_id=payload.user_id,
        zawiya_id=payload.zawiya_id
    )

@router.get("/update/notification/level")
async def _update_notification_level(payload: ZawiyaSubscriptionNotificationLevel):
    return await zawiya_subscription_crud.update_level(
        user_id=payload.user_id,
        zawiya_id=payload.zawiya_id,
        level=payload.notification_level
    )