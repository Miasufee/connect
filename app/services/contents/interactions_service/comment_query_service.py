from beanie import PydanticObjectId
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
            filters={
                "post_id": post_id,
                "parent_comment_id": None,
                "is_shadow_banned": False
            },
            order_by="-created_at",
            skip=skip,
            limit=per_page,
        )

        total = post_comment_crud.count(
            filters={
                "post_id": post_id,
                "parent_comment_id": None,
                "is_shadow_banned": False
            }
        )

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
            filters={
                "parent_comment_id": parent_comment_id,
                "is_shadow_banned": True
            },
            order_by="created_at",
            limit=limit,
        )
