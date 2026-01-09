from fastapi import APIRouter
from beanie import PydanticObjectId

from app.core.utils.dependencies import RegularUser
from app.services.contents.interactions_service.comment_reaction_service import CommentReactionService

comment_reaction_router = APIRouter(prefix="/comments", tags=["Comment Reactions"])


@comment_reaction_router.post("/{comment_id}/like")
async def toggle_like(
    comment_id: PydanticObjectId,
    user_id: RegularUser = None,
):
    return await CommentReactionService.toggle_like(
        comment_id=comment_id,
        user_id=user_id.id,
    )


@comment_reaction_router.post("/{comment_id}/dislike")
async def toggle_dislike(
    comment_id: PydanticObjectId,
    user_id: RegularUser = None,
):
    return await CommentReactionService.toggle_dislike(
        comment_id=comment_id,
        user_id=user_id.id,
    )
