from beanie import Document

from app.models import TimestampMixin, SoftDeleteMixin, UserIdMixin, ZawiyaIdMixin, PostMixin, GroupIdMixin


class ZawiyaPost(
    Document,
    TimestampMixin,
    SoftDeleteMixin,
    UserIdMixin,
    ZawiyaIdMixin,
    PostMixin

):
    pinned: bool = False

    class Settings:
        name = "zawiya_posts"
        indexes = [
            [("zawiya_id", 1), ("published", 1), ("created_at", -1)],
            "content_type",
            "visibility",
        ]

class GroupPost(
    Document,
    TimestampMixin,
    SoftDeleteMixin,
    UserIdMixin,
    GroupIdMixin,
    PostMixin
):
    is_pinned: bool = False

    class Settings:
        name = "group_posts"
        indexes = [
            [("group_id", 1), ("published", 1), ("created_at", -1)],
            "content_type",
            "visibility",
            "is_pinned",
        ]
