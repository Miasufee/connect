from fastapi import APIRouter
from beanie import PydanticObjectId

from app.services.contents.interactions_service.comment_ranking_service import CommentRankingService

comment_ranking_router = APIRouter(prefix="/comments", tags=["Comment Ranking"])


@comment_ranking_router.get("/post/{post_id}/hot")
async def _hot_comments(
    post_id: PydanticObjectId,
    limit: int = 20,
):
    return await CommentRankingService.hot_comments(
        post_id=post_id,
        limit=limit,
    )
