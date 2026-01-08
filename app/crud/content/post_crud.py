from typing import List, Optional
from beanie import PydanticObjectId, SortDirection
from app.crud import CrudBase
from app.models import ZawiyaPost, GroupPost, VisibilityStatus


# ----------------- ZAWIYA POSTS -----------------
class ZawiyaPostCrud(CrudBase[ZawiyaPost]):
    """ Zawiya Post Crud Management """
    def __init__(self):
        super().__init__(ZawiyaPost)

    async def feed_for_you(self, page: int = 1, per_page: int = 20):
        """ For You feed with live boost, engagement, media richness, and recency."""
        pipeline = [
            # Only published public posts
            {"$match": {"is_deleted": False, "published": True, "visibility": "PUBLIC"}},

            # Add computed fields
            {"$addFields": {
                # Basic engagement score
                "score": {"$add": ["$like_count", "$view_count", "$dislike_count"]},
                # Boost pinned/live posts
                "live_boost": {"$cond": [{"$eq": ["$pinned", True]}, 10, 0]},
                # Media richness score (count number of attached media)
                "media_count": {"$add": [
                    {"$size": {"$ifNull": ["$video_ids", []]}},
                    {"$size": {"$ifNull": ["$audio_ids", []]}},
                    {"$size": {"$ifNull": ["$image_ids", []]}}
                ]},
            }},

            # Sort by live boost -> engagement -> media richness -> newest first
            {"$sort": {"live_boost": -1, "score": -1, "media_count": -1, "created_at": -1}},

            # Pagination
            {"$skip": (page - 1) * per_page},
            {"$limit": per_page},
        ]
        return await self.aggregate(pipeline)

    async def feed_following(
        self,
        following_zawiya_ids: List[PydanticObjectId],
        page: int = 1,
        per_page: int = 20
    ) -> dict:
        """Posts from followed zawiyas."""
        filters = {"zawiya_id": {"$in": following_zawiya_ids}, "is_deleted": False, "published": True}
        return await self.paginate(page=page, per_page=per_page, filters=filters, order_by="created_at")

    async def feed_live(
        self,
        live_status_only: bool = True,
        page: int = 1,
        per_page: int = 20
    ) -> dict:
        """Live or recorded posts."""
        filters = {"is_deleted": False, "published": True}
        return await self.paginate(page=page, per_page=per_page, filters=filters, order_by="created_at")

    async def feed_by_zawiya(
        self,
        zawiya_id: PydanticObjectId,
        page: int = 1,
        per_page: int = 20
    ) -> dict:
        """Posts for a specific Zawiya."""
        filters = {"zawiya_id": zawiya_id, "is_deleted": False, "published": True}
        return await self.paginate(page=page, per_page=per_page, filters=filters, order_by="created_at")


# ----------------- GROUP POSTS -----------------
class GroupPostCrud(CrudBase[GroupPost]):
    """ Group Crud Management """
    def __init__(self):
        super().__init__(GroupPost)

    async def feed_by_group(
        self,
        group_id: PydanticObjectId,
        page: int = 1,
        per_page: int = 20
    ) -> dict:
        """ group feed with pinned posts first."""
        # Pinned posts first
        pinned = await self.get_multi(
            filters={"group_id": group_id, "is_pinned": True, "is_deleted": False, "published": True},
            order_by=[("created_at", SortDirection.DESCENDING)]
        )
        # Normal posts
        normal = await self.get_multi(
            filters={"group_id": group_id, "is_pinned": False, "is_deleted": False, "published": True},
            order_by=[("created_at", SortDirection.DESCENDING)],
            skip=(page-1)*per_page,
            limit=per_page
        )
        return {"items": pinned + normal, "total": len(pinned) + len(normal), "page": page, "per_page": per_page}


# ----------------- SINGLETONS -----------------
zawiya_post_crud = ZawiyaPostCrud()
group_post_crud = GroupPostCrud()