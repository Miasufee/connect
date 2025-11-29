from enum import Enum
from typing import Optional
from beanie import Document, PydanticObjectId
from pydantic import Field

from app.models.models_base import TimestampMixin, SoftDeleteMixin, UserIdMixin


class VideoCommentReactionType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"


class VideoCommentReaction(Document, TimestampMixin):
    user_id: PydanticObjectId
    comment_id: PydanticObjectId
    reaction: VideoCommentReactionType

    class Settings:
        name = "video_comment_reactions"
        indexes = [
            ("user_id", "comment_id"),
        ]
class LiveStreamCommentReactionType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"


class LiveStreamCommentReaction(Document, TimestampMixin):
    user_id: PydanticObjectId
    comment_id: PydanticObjectId
    reaction: LiveStreamCommentReactionType

    class Settings:
        name = "livestream_comment_reactions"
        indexes = [
            ("user_id", "comment_id"),
        ]


class VideoComment(
    Document,
    TimestampMixin,
    SoftDeleteMixin,
    UserIdMixin
):
    """Comment model for video documents"""

    video_id: PydanticObjectId
    parent_comment_id: Optional[PydanticObjectId] = None

    content: str = Field(..., min_length=1, max_length=2000)

    like_count: int = 0
    dislike_count: int = 0
    reply_count: int = 0

    depth: int = Field(default=0, description="Reply nesting depth, max 3")

    class Settings:
        name = "video_comments"
        indexes = [
            "video_id",
            "user_id",
            "parent_comment_id",
        ]

class LiveStreamComment(
    Document,
    TimestampMixin,
    SoftDeleteMixin,
    UserIdMixin
):
    """Comment model for livestream documents"""

    livestream_id: PydanticObjectId
    parent_comment_id: Optional[PydanticObjectId] = None

    content: str = Field(..., min_length=1, max_length=2000)

    like_count: int = 0
    dislike_count: int = 0
    reply_count: int = 0

    depth: int = Field(default=0, description="Reply nesting depth, max 3")

    class Settings:
        name = "livestream_comments"
        indexes = [
            "livestream_id",
            "user_id",
            "parent_comment_id",
        ]
