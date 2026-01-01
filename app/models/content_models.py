from typing import Optional

from beanie import Document, PydanticObjectId

from app.models import TimestampMixin, VisibilityStatus


class Content(Document, TimestampMixin):
    zawiya_id: PydanticObjectId
    group_id: Optional[PydanticObjectId] = None  # ← OPTIONAL

    author_id: PydanticObjectId

    content_type: ContentType
    title: Optional[str] = None
    text: Optional[str] = None

    visibility: VisibilityStatus = VisibilityStatus.PUBLIC

    class Settings:
        name = "contents"
        indexes = [
            "zawiya_id",
            "group_id",
            "content_type",
        ]
