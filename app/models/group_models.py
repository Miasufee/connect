from beanie import Document, PydanticObjectId

from app.models import TimestampMixin, ZawiyaIdMixin, UserIdMixin, TitleMixin, DescriptionMixin, VisibilityStatus, \
    GroupRole


class Group(Document, TimestampMixin, ZawiyaIdMixin, UserIdMixin, TitleMixin, DescriptionMixin):
    created_by: PydanticObjectId
    visibility: VisibilityStatus = VisibilityStatus.PRIVATE

    class Settings:
        name = "groups"
        indexes = ["zawiya_id"]

class GroupProfile(Document, TimestampMixin):
    group_id: PydanticObjectId
    averter_url: str

class GroupMember(Document, TimestampMixin):
    group_id: PydanticObjectId
    user_id: PydanticObjectId
    group_role: GroupRole = GroupRole.MEMBER
    can_post: bool = False
    can_stream: bool = False

    class Settings:
        name = "group_members"
        indexes = [
            ("group_id", "user_id"),
        ]
