from beanie import Document, PydanticObjectId

from app.models import TimestampMixin, VisibilityStatus, ContentType, ZawiyaIdMixin, GroupIdMixin, UserIdMixin


class Post(Document, TimestampMixin, ZawiyaIdMixin, GroupIdMixin, UserIdMixin):
    content_id: PydanticObjectId # video live-stream image
    content_type: ContentType
    is_deleted: bool = False
    is_pinned: bool = False
    published: bool = False
    like_count: int = 0
    dislike_count: int = 0

    visibility: VisibilityStatus = VisibilityStatus.PRIVATE

    class Settings:
        name = "contents"
        indexes = [
            "zawiya_id",
            "group_id",
            "content_type",
        ]
