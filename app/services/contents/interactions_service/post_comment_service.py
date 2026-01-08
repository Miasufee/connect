from beanie import PydanticObjectId
from app.crud.interactions_cruds.post_comment_crud import post_comment_crud
from app.crud.content.post_crud import zawiya_post_crud
from app.crud.interactions_cruds.post_reaction_crud import post_reaction_crud
from app.models import ZawiyaPost, ReactionType
from app.models.interactions_models import PostComment, PostReaction


class PostCommentService:
    """ Post Comment Service """

    # -------------------------
    # CREATE ROOT COMMENT
    # -------------------------
    @staticmethod
    async def create_comment(
        *,
        post_id: PydanticObjectId,
        user_id: PydanticObjectId,
        content: str,
    ) -> PostComment:

        comment = await post_comment_crud.create(
            post_id=post_id,
            user_id=user_id,
            content=content,
            depth=0,
            parent_comment_id=None,
        )

        # Increment post comment count
        await zawiya_post_crud.get_one(
            ZawiyaPost.id == post_id
        ).update({"$inc": {"comment_count": 1}})

        return comment

    # -------------------------
    # REPLY TO COMMENT
    # -------------------------
    @staticmethod
    async def reply_to_comment(
        *,
        post_id: PydanticObjectId,
        parent_comment_id: PydanticObjectId,
        user_id: PydanticObjectId,
        content: str,
        max_depth: int = 3,
    ) -> PostComment:

        parent = await post_comment_crud.get_by_id(parent_comment_id)
        if not parent:
            raise ValueError("Parent comment not found")

        if parent.depth >= max_depth:
            raise ValueError("Maximum comment depth reached")

        reply = await post_comment_crud.create(
            post_id=post_id,
            user_id=user_id,
            content=content,
            parent_comment_id=parent.id,
            depth=parent.depth + 1,
        )

        # Increment reply count on parent
        await post_comment_crud.get_one(
            PostComment.id == parent.id
        ).update({"$inc": {"reply_count": 1}})

        # Increment total post comments
        await zawiya_post_crud.get_one(
            ZawiyaPost.id == post_id
        ).update({"$inc": {"comment_count": 1}})

        return reply

    # -------------------------
    # DELETE COMMENT
    # -------------------------
    @staticmethod
    async def delete_comment(
        *,
        comment_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ) -> bool:

        comment = await post_comment_crud.get_by_id(comment_id)
        if not comment:
            return False

        if comment.user_id != user_id:
            raise PermissionError("Not allowed")

        # Soft delete pattern
        comment.content = "[deleted]"
        await comment.save()

        return True
    # -------------------------
    # TOGGLE COMMENT LIKE
    # -------------------------
    @staticmethod
    async def toggle_comment_like(
        *,
        comment_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ) -> str:

        existing = await post_reaction_crud.get_one(
            PostReaction.post_id == comment_id,
            PostReaction.user_id == user_id,
        )

        if not existing:
            await post_reaction_crud.create(
                post_id=comment_id,
                user_id=user_id,
                reaction=ReactionType.LIKE,
            )

            await post_comment_crud.get_one(
                PostComment.id == comment_id
            ).update({"$inc": {"like_count": 1}})
            return "liked"

        if existing.reaction == ReactionType.LIKE:
            await existing.delete()
            await post_comment_crud.get_one(
                PostComment.id == comment_id
            ).update({"$inc": {"like_count": -1}})
            return "unliked"

        return "noop"
    @staticmethod
    async def get_post_comments(post_id: PydanticObjectId):
        return await post_comment_crud.get_multi(
            PostComment.post_id == post_id,
            PostComment.parent_comment_id == None,
            order_by="-created_at",
        )
    @staticmethod
    async def get_replies(parent_comment_id: PydanticObjectId):
        return await post_comment_crud.get_multi(
            PostComment.parent_comment_id == parent_comment_id,
            order_by="created_at",
        )

class CommentQueryService:

    @staticmethod
    async def get_root_comments(
        *,
        post_id: PydanticObjectId,
        page: int = 1,
        per_page: int = 20,
    ):
        skip = (page - 1) * per_page

        items = await post_comment_crud.get_multi(
            PostComment.post_id == post_id,
            PostComment.parent_comment_id == None,
            order_by="-created_at",
            skip=skip,
            limit=per_page,
        )

        total = await PostComment.find(
            PostComment.post_id == post_id,
            PostComment.parent_comment_id == None,
        ).count()

        return {
            "items": items,
            "page": page,
            "per_page": per_page,
            "total": total,
        }
    @staticmethod
    async def get_replies(
        *,
        parent_comment_id: PydanticObjectId,
        limit: int = 10,
    ):
        return await post_comment_crud.get_multi(
            PostComment.parent_comment_id == parent_comment_id,
            order_by="created_at",
            limit=limit,
        )

class CommentReactionService:

    @staticmethod
    async def toggle_like(
        *,
        comment_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ) -> str:

        existing = await PostReaction.find_one(
            PostReaction.post_id == comment_id,
            PostReaction.user_id == user_id,
        )

        if not existing:
            await post_reaction_crud.create(
                post_id=comment_id,
                user_id=user_id,
                reaction=ReactionType.LIKE,
            )

            await post_reaction_crud.get_one(
                PostComment.id == comment_id
            ).update({"$inc": {"like_count": 1}})
            return "liked"

        if existing.reaction == ReactionType.LIKE:
            await existing.delete()
            await post_comment_crud(
                PostComment.id == comment_id
            ).update({"$inc": {"like_count": -1}})
            return "unliked"

        if existing.reaction == ReactionType.DISLIKE:
            existing.reaction = ReactionType.LIKE
            await existing.save()

            await post_comment_crud.get_one(
                PostComment.id == comment_id
            ).update(
                {"$inc": {"like_count": 1, "dislike_count": -1}}
            )
            return "switched_to_like"
        return None

    @staticmethod
    async def toggle_dislike(
        *,
        comment_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ) -> str:

        existing = await PostReaction.find_one(
            PostReaction.post_id == comment_id,
            PostReaction.user_id == user_id,
        )

        if not existing:
            await PostReaction(
                post_id=comment_id,
                user_id=user_id,
                reaction=ReactionType.DISLIKE,
            ).insert()

            await post_comment_crud.get_one(
                PostComment.id == comment_id
            ).update({"$inc": {"dislike_count": 1}})
            return "disliked"

        if existing.reaction == ReactionType.DISLIKE:
            await existing.delete()
            await post_comment_crud.get_one(
                PostComment.id == comment_id
            ).update({"$inc": {"dislike_count": -1}})
            return "undisliked"

        if existing.reaction == ReactionType.LIKE:
            existing.reaction = ReactionType.DISLIKE
            await existing.save()

            await post_comment_crud.get_one(
                PostComment.id == comment_id
            ).update(
                {"$inc": {"like_count": -1, "dislike_count": 1}}
            )
            return "switched_to_dislike"
        return None


class CommentModerationService:

    @staticmethod
    async def shadow_ban(comment_id: PydanticObjectId):
        await post_comment_crud.get_one(
            PostComment.id == comment_id
        ).update({"$set": {"is_shadow_banned": True}})

    @staticmethod
    async def unshadow_ban(comment_id: PydanticObjectId):
        await post_comment_crud.get_one(
            PostComment.id == comment_id
        ).update({"$set": {"is_shadow_banned": False}})
