from fastapi import APIRouter, Depends
from beanie import PydanticObjectId

from app.core.utils.dependencies import RegularUser
from app.services.contents.interactions_service.post_reaction_service import PostCommentService

comment_router = APIRouter(prefix="/comments", tags=["Comments"])


@comment_router.post("/{post_id}")
async def create_comment(
    post_id: PydanticObjectId,
    content: str,
    user_id: RegularUser = None,
):
    return await PostCommentService.create_comment(
        post_id=post_id,
        user_id=user_id.id,
        content=content,
    )


@comment_router.post("/{post_id}/reply/{parent_comment_id}")
async def reply_to_comment(
    post_id: PydanticObjectId,
    parent_comment_id: PydanticObjectId,
    content: str,
    user_id: RegularUser = None,
):
    return await PostCommentService.reply_to_comment(
        post_id=post_id,
        parent_comment_id=parent_comment_id,
        user_id=user_id.id,
        content=content,
    )


@comment_router.delete("/{comment_id}")
async def delete_comment(
    comment_id: PydanticObjectId,
    user_id: RegularUser = None,
):
    return await PostCommentService.delete_comment(
        comment_id=comment_id,
        user_id=user_id.id,
    )
