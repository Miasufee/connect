from fastapi import APIRouter
from beanie import PydanticObjectId

from app.services.contents.interactions_service.comment_query_service import CommentQueryService

comment_query_router = APIRouter(prefix="/comments", tags=["Comment Queries"])


@comment_query_router.get("/post/{post_id}")
async def _get_root_comments(
    post_id: PydanticObjectId,
    page: int = 1,
    per_page: int = 20,
):
    return await CommentQueryService.get_root_comments(
        post_id=post_id,
        page=page,
        per_page=per_page,
    )


@comment_query_router.get("/replies/{parent_comment_id}")
async def _get_replies(
    parent_comment_id: PydanticObjectId,
    limit: int = 10,
):
    return await CommentQueryService.get_replies(
        parent_comment_id=parent_comment_id,
        limit=limit,
    )
