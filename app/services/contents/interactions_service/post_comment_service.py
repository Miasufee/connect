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
