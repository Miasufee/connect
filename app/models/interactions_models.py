from beanie import Document, PydanticObjectId

from app.models import TimestampMixin, ReactionType


class PostReaction(Document, TimestampMixin):
    post_id: PydanticObjectId
    user_id: PydanticObjectId
    reaction: ReactionType

    class Settings:
        name = "post_reactions"
        indexes = [
            [("post_id", 1), ("user_id", 1)],
            "post_id",
            "user_id",
        ]
class PostComment(Document, TimestampMixin):
    post_id: PydanticObjectId
    user_id: PydanticObjectId

    content: str
    parent_comment_id: PydanticObjectId | None = None
    depth: int = 0
    is_shadow_banned: bool = False

    like_count: int = 0
    reply_count: int = 0

    class Settings:
        name = "post_comments"
        indexes = [
            "post_id",
            "user_id",
            "parent_comment_id",
        ]
class PostShare(Document, TimestampMixin):
    post_id: PydanticObjectId
    user_id: PydanticObjectId
    platform: str | None = None
    target_user_id: PydanticObjectId | None = None

    class Settings:
        name = "post_shares"
        indexes = [
            "post_id",
            "user_id",
        ]
