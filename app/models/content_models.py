from __future__ import annotations

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.models import (
    TimestampMixin,
    SoftDeleteMixin,
    VisibilityStatus,
    ContentType,
    UserIdMixin, ZawiyaIdMixin, GroupIdMixin,
)


class PostBase(
    Document,
    TimestampMixin,
    SoftDeleteMixin,
    UserIdMixin,
):
    """
    A post is a wrapper around content (video, image, audio, stream).
    """

    content_id: PydanticObjectId
    content_type: ContentType

    published: bool = False
    visibility: VisibilityStatus = VisibilityStatus.PRIVATE

    like_count: int = 0
    dislike_count: int = 0
    comment_count: int = 0

    class Settings:
        is_root = True


class ZawiyaPost(PostBase, ZawiyaIdMixin):
    """
    Post published under a Zawiya (channel).
    """
    pinned: bool = False

    class Settings:
        name = "zawiya_posts"
        indexes = [
            "zawiya_id",
            "content_type",
            "published",
            "visibility",
        ]



class GroupPost(PostBase, GroupIdMixin):
    """
    Post published inside a Group.
    """

    is_pinned: bool = False

    class Settings:
        name = "group_posts"
        indexes = [
            "group_id",
            "content_type",
            "published",
            "visibility",
            "is_pinned",
        ]
