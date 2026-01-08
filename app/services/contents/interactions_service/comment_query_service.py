from beanie import PydanticObjectId
from app.models.interactions_models import PostComment
from app.crud.interactions_cruds.post_comment_crud import post_comment_crud


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
            PostComment.is_shadow_banned == False,
            order_by="-created_at",
            skip=skip,
            limit=per_page,
        )

        total = await PostComment.find(
            PostComment.post_id == post_id,
            PostComment.parent_comment_id == None,
            PostComment.is_shadow_banned == False,
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
            PostComment.is_shadow_banned == False,
            order_by="created_at",
            limit=limit,
        )
