from beanie import PydanticObjectId

from app.crud.interactions_cruds.post_comment_crud import post_comment_crud


class CommentRankingService:

    @staticmethod
    async def hot_comments(post_id: PydanticObjectId, limit: int = 20):
        return await post_comment_crud.hot_comments(post_id, limit)
