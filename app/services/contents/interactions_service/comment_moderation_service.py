from beanie import PydanticObjectId
from app.models.interactions_models import PostComment
from app.crud.interactions_cruds.post_comment_crud import post_comment_crud


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
