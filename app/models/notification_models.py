from beanie import Document, PydanticObjectId

from app.models import TimestampMixin


class Notification(Document, TimestampMixin):
    user_id: PydanticObjectId
    type: str  # reply, mention, like
    actor_id: PydanticObjectId
    post_id: PydanticObjectId
    comment_id: PydanticObjectId | None = None
    is_read: bool = False
