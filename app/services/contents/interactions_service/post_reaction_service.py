from beanie import PydanticObjectId
from app.crud.interactions_cruds.post_comment_crud import post_comment_crud
from app.crud.content.post_crud import zawiya_post_crud
from app.models import ZawiyaPost
from app.models.interactions_models import PostComment


class PostCommentService:

    @staticmethod
    async def create_comment(
        *,
        post_id: PydanticObjectId,
        user_id: PydanticObjectId,
        content: str,
    ):
        comment = await post_comment_crud.create(
            post_id=post_id,
            user_id=user_id,
            content=content,
            depth=0,
            parent_comment_id=None,
        )

        await zawiya_post_crud.get_one(
            ZawiyaPost.id == post_id
        ).update({"$inc": {"comment_count": 1}})

        return comment

    @staticmethod
    async def reply_to_comment(
        *,
        post_id: PydanticObjectId,
        parent_comment_id: PydanticObjectId,
        user_id: PydanticObjectId,
        content: str,
        max_depth: int = 3,
    ):
        parent = await post_comment_crud.get_by_id(parent_comment_id)
        if not parent or parent.is_deleted:
            raise ValueError("Parent comment not found")

        if parent.depth >= max_depth:
            raise ValueError("Max depth reached")

        reply = await post_comment_crud.create(
            post_id=post_id,
            user_id=user_id,
            content=content,
            parent_comment_id=parent.id,
            depth=parent.depth + 1,
        )

        await post_comment_crud.get_one(
            PostComment.id == parent.id
        ).update({"$inc": {"reply_count": 1}})

        await zawiya_post_crud.get_one(
            ZawiyaPost.id == post_id
        ).update({"$inc": {"comment_count": 1}})

        return reply

    @staticmethod
    async def delete_comment(
        *,
        comment_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ):
        comment = await post_comment_crud.get_by_id(comment_id)
        if not comment:
            return False

        if comment.user_id != user_id:
            raise PermissionError("Not allowed")

        await post_comment_crud.get_one(
            PostComment.id == comment_id
        ).update({
            "$set": {
                "is_deleted": True,
                "content": "[deleted]",
            }
        })

        return True
