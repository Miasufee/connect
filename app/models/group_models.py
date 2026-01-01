from typing import Optional

from beanie import Document, PydanticObjectId

from app.models import TimestampMixin


class Group(Document, TimestampMixin):
    zawiya_id: PydanticObjectId

    name: str
    description: Optional[str] = None

    class Settings:
        name = "groups"
        indexes = ["zawiya_id"]

class GroupMember(Document, TimestampMixin):
    group_id: PydanticObjectId
    user_id: PydanticObjectId
    can_post: bool = False
    can_stream: bool = False
    is_admin: bool = False

    class Settings:
        name = "group_members"
        indexes = [
            ("group_id", "user_id"),
        ]
