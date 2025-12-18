from fastapi import APIRouter, status
from beanie import PydanticObjectId

from app.core.utils.dependencies import RegularUser
from app.schemas.zawiya.zawiya_subscription_schema import ZawiyaSubscriptionRequest, ZawiyaSubscriptionResponse
from app.services.zawiya.zawiya_subscription_service import zawiya_subscription_service

zawiya_subscription_router = APIRouter(prefix="/subscriptions")


@zawiya_subscription_router.post(
    "/{zawiya_id}/subscribe",
    response_model=ZawiyaSubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def subscribe(
    zawiya_id: PydanticObjectId,
    payload: ZawiyaSubscriptionRequest,
    user_id: RegularUser = None
):
    subscription = await zawiya_subscription_service.subscribe_user(
        user_id.id, zawiya_id, payload.level
    )
    return ZawiyaSubscriptionResponse(
        success=True,
        subscription_id=subscription.id,
        message="Subscribed successfully"
    )


@zawiya_subscription_router.delete(
    "/{zawiya_id}/unsubscribe",
    response_model=ZawiyaSubscriptionResponse,
    status_code=status.HTTP_200_OK,
)
async def unsubscribe(
    zawiya_id: PydanticObjectId,
    user_id: RegularUser = None
):
    await zawiya_subscription_service.unsubscribe_user(user_id.id, zawiya_id)
    return ZawiyaSubscriptionResponse(
        success=True,
        subscription_id=None,
        message="Unsubscribed successfully"
    )


@zawiya_subscription_router.patch(
    "/{zawiya_id}/level",
    response_model=ZawiyaSubscriptionResponse,
    status_code=status.HTTP_200_OK,
)
async def update_notification_level(
    zawiya_id: PydanticObjectId,
    payload: ZawiyaSubscriptionRequest,
    user_id: RegularUser = None
):
    subscription = await zawiya_subscription_service.change_notification_level(
        user_id.id, zawiya_id, payload.level
    )
    return ZawiyaSubscriptionResponse(
        success=True,
        subscription_id=subscription.id,
        message="Notification level updated"
    )


@zawiya_subscription_router.get(
    "/{zawiya_id}/check",
    response_model=ZawiyaSubscriptionResponse,
    status_code=status.HTTP_200_OK,
)
async def check_subscription(
    zawiya_id: PydanticObjectId,
    user_id: RegularUser = None
):
    subscription = await zawiya_subscription_service.check_subscription(user_id.id, zawiya_id)
    return ZawiyaSubscriptionResponse(
        success=True,
        subscription_id=subscription.id if subscription else None,
        message="Subscribed" if subscription else "Not subscribed"
    )


@zawiya_subscription_router.get(
    "/{zawiya_id}/count",
    status_code=status.HTTP_200_OK,
)
async def total_subscribers(zawiya_id: PydanticObjectId):
    total = await zawiya_subscription_service.count_subscribers(zawiya_id)
    return {"success": True, "zawiya_id": zawiya_id, "total_subscribers": total}
