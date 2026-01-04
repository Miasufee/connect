from typing import Optional, Dict, Any
from beanie import PydanticObjectId

from app.crud import CrudBase
from app.models import Post, ContentType, VisibilityStatus


class PostCrud(CrudBase[Post]):
    def __init__(self):
        super().__init__(Post)

    # ---------- CREATE ----------

    async def create_post(
        self,
        *,
        zawiya_id: PydanticObjectId,
        group_id: Optional[PydanticObjectId],
        user_id: PydanticObjectId,
        content_id: PydanticObjectId,
        content_type: ContentType,
        visibility: VisibilityStatus = VisibilityStatus.PRIVATE,
        published: bool = False,
    ) -> Post:
        return await self.create(
            zawiya_id=zawiya_id,
            group_id=group_id,
            user_id=user_id,
            content_id=content_id,
            content_type=content_type,
            visibility=visibility,
            published=published,
        )

    # ---------- READ ----------

    async def get_by_id(self, post_id: PydanticObjectId) -> Optional[Post]:
        return await self.get(post_id)

    async def get_zawiya_posts(
        self,
        zawiya_id: PydanticObjectId,
        *,
        page: int = 1,
        per_page: int = 30,
    ) -> Dict[str, Any]:
        filters = {
            "zawiya_id": zawiya_id,
            "is_deleted": False,
            "published": True,
        }

        return await self.paginate(
            page=page,
            per_page=per_page,
            filters=filters,
            order_by="created_at"
,
        )

    async def get_group_posts(
        self,
        group_id: PydanticObjectId,
        *,
        page: int = 1,
        per_page: int = 30,
    ) -> Dict[str, Any]:
        return await self.paginate(
            page=page,
            per_page=per_page,
            filters={
                "group_id": group_id,
                "is_deleted": False,
                "published": True,
            },
            oorder_by="created_at"
,
        )

    async def get_user_posts(
        self,
        user_id: PydanticObjectId,
        *,
        page: int = 1,
        per_page: int = 30,
    ) -> dict[str, Any]:
        return await self.paginate(
            page=page,
            per_page=per_page,
            filters={
                "user_id": user_id,
                "is_deleted": False,
            },
            order_by="created_at"
,
        )

    # ---------- UPDATE ----------

    async def publish(self, post_id: PydanticObjectId) -> bool:
        post = await self.get(post_id)
        if not post or post.is_deleted:
            return False

        post.published = True
        await post.save()
        return True

    async def unpublish(self, post_id: PydanticObjectId) -> bool:
        post = await self.get(post_id)
        if not post:
            return False

        post.published = False
        await post.save()
        return True

    async def pin(self, post_id: PydanticObjectId) -> bool:
        post = await self.get(post_id)
        if not post or post.is_deleted:
            return False

        post.is_pinned = True
        await post.save()
        return True

    async def unpin(self, post_id: PydanticObjectId) -> bool:
        post = await self.get(post_id)
        if not post:
            return False

        post.is_pinned = False
        await post.save()
        return True

    async def update_visibility(
        self,
        post_id: PydanticObjectId,
        visibility: VisibilityStatus,
    ) -> bool:
        post = await self.get(post_id)
        if not post:
            return False

        post.visibility = visibility
        await post.save()
        return True

    # ---------- COUNTERS ----------

    # ---------- COUNTERS ----------

    async def increment_like(self, post_id: PydanticObjectId, value: int = 1):
        await self.model.find_one({"_id": post_id}).update_one(
            {"$inc": {"like_count": value}}
        )

    async def increment_dislike(self, post_id: PydanticObjectId, value: int = 1):
        await self.model.find_one({"_id": post_id}).update_one(
            {"$inc": {"dislike_count": value}}
        )
    # ---------- DELETE ----------

    async def soft_delete_post(self, post_id: PydanticObjectId) -> bool:
        post = await self.get(post_id)
        if not post or post.is_deleted:
            return False

        post.is_deleted = True
        await post.save()
        return True

    async def restore_post(self, post_id: PydanticObjectId) -> bool:
        post = await self.get(post_id)
        if not post or not post.is_deleted:
            return False

        post.is_deleted = False
        await post.save()
        return True

post_crud = PostCrud()