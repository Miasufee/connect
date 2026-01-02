from typing import List
from bson import ObjectId
from beanie import SortDirection

from app.services.subscription_service import SubscriptionService
from app.services.livestream_service import LiveStreamService
from app.crud.crud_content import ContentCrud
from app.models import VisibilityStatus

class ContentService(ContentCrud):
    def __init__(self):
        super().__init__()

    # ---------------- FOLLOWING FEED ----------------
    async def get_following_feed(
        self,
        user_id: ObjectId,
        *,
        skip: int = 0,
        limit: int = 20,
    ):
        from app.models import ZawiyaSubscription

        # 1. Get followed zawiyas
        subscriptions = await ZawiyaSubscription.find(
            {
                "user_id": user_id,
                "is_deleted": False,
            }
        ).to_list()

        zawiya_ids = [s.zawiya_id for s in subscriptions]

        if not zawiya_ids:
            return []

        # 2. Get content from followed zawiyas
        return await self.list(
            filters={
                "zawiya_id": {"$in": zawiya_ids},
                "visibility": VisibilityStatus.PUBLIC,
                "is_deleted": False,
            },
            skip=skip,
            limit=limit,
            order_desc=True,
        )

    # ---------------- ZAWIYA FEED ----------------
    async def get_zawiya_feed(
        self,
        zawiya_id: ObjectId,
        *,
        skip: int = 0,
        limit: int = 20,
    ):
        return await self.list(
            filters={
                "zawiya_id": zawiya_id,
                "visibility": VisibilityStatus.PUBLIC,
                "is_deleted": False,
            },
            skip=skip,
            limit=limit,
            order_desc=True,
        )
class FeedService:
    def __init__(self):
        self.subscriptions = SubscriptionService()
        self.content = ContentService()
        self.livestreams = LiveStreamService()

    # ---------------- HOME FEED ----------------
    async def get_home_feed(
        self,
        user_id: ObjectId,
        *,
        skip: int = 0,
        limit: int = 20,
    ):
        # 1. Followed zawiyas
        followed_zawiyas = await self.subscriptions.get_followed_zawiyas(user_id)

        # 2. Live streams (highest priority)
        live_streams = await self.livestreams.get_live_streams_for_user(
            followed_zawiyas
        )

        # 3. Posts from followed zawiyas
        posts = await self.content.get_following_feed(
            user_id=user_id,
            skip=skip,
            limit=limit,
        )

        return {
            "live": live_streams,
            "posts": posts,
        }
class ForYouService:
    def __init__(self):
        self.content = ContentService()

    async def get_for_you_feed(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
    ):
        """
        For now:
        - Public content
        - Latest first
        Later:
        - Ranking
        - Engagement
        - Personalization
        """

        return await self.content.list(
            filters={
                "visibility": VisibilityStatus.PUBLIC,
                "is_deleted": False,
            },
            skip=skip,
            limit=limit,
            order_desc=True,
        )
