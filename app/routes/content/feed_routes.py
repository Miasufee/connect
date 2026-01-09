from fastapi import APIRouter, Query
from typing import List
from beanie import PydanticObjectId

from app.core.utils.dependencies import RegularUser
from app.services.contents.feed_service import UnifiedFeedService

feed_router = APIRouter()


@feed_router.get("/zawiya/for-you")
async def for_you_feed(
        user_id: RegularUser = None,
        page: int = 1,
        per_page: int = 20
):
    return await UnifiedFeedService.for_you(
        user_id=user_id.id,
        page=page,
        per_page=per_page
    )


@feed_router.get("/zawiya/following")
async def following_feed(
        user_id: RegularUser = None,
        following_zawiyas: List[PydanticObjectId] = Query([]),
        page: int = 1, per_page: int = 20
):
    return await UnifiedFeedService.following(
        user_id=user_id.id,
        following_zawiyas=following_zawiyas,
        page=page,
        per_page=per_page
    )


@feed_router.get("/zawiya/live")
async def live_feed(user_id: RegularUser = None, page: int = 1, per_page: int = 20):
    return await UnifiedFeedService.live(
        user_id=user_id.id,
        page=page,
        per_page=per_page)


@feed_router.get("/zawiya/{zawiya_id}/feed")
async def feed_by_zawiya(zawiya_id: PydanticObjectId, page: int = 1, per_page: int = 20):
    return await UnifiedFeedService.by_zawiya(
        zawiya_id=zawiya_id,
        page=page,
        per_page=per_page
    )


@feed_router.get("/group/{group_id}/feed")
async def group_feed(
        group_id: PydanticObjectId,
        page: int = 1,
        per_page: int = 20
):
    return await UnifiedFeedService.by_group(
        group_id=group_id,
        page=page,
        per_page=per_page
    )
