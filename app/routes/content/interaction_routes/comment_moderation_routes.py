from fastapi import APIRouter
from beanie import PydanticObjectId

from app.services.contents.interactions_service.comment_moderation_service import CommentModerationService

comment_moderation_router = APIRouter(prefix="/comments/moderation", tags=["Comment Moderation"])


@comment_moderation_router.post("/{comment_id}/shadow-ban")
async def _shadow_ban(comment_id: PydanticObjectId):
    await CommentModerationService.shadow_ban(comment_id)
    return {"status": "shadow_banned"}


@comment_moderation_router.post("/{comment_id}/unshadow-ban")
async def _unshadow_ban(comment_id: PydanticObjectId):
    await CommentModerationService.unshadow_ban(comment_id)
    return {"status": "unshadow_banned"}
