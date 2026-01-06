from beanie import Document, PydanticObjectId

from app.models import TimestampMixin, ZawiyaIdMixin, UserIdMixin, TitleMixin, DescriptionMixin, VisibilityStatus, \
    GroupRole, SoftDeleteMixin, InviteStatus, JoinRequestStatus


class Group(Document, TimestampMixin, SoftDeleteMixin, ZawiyaIdMixin, UserIdMixin, TitleMixin, DescriptionMixin):
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


class GroupInvite(Document, TimestampMixin):
    group_id: PydanticObjectId
    inviter_id: PydanticObjectId
    invitee_id: PydanticObjectId
    status: InviteStatus = InviteStatus.PENDING

    class Settings:
        name = "group_invites"
        indexes = [("group_id", "invitee_id")]


class GroupJoinRequest(Document, TimestampMixin):
    group_id: PydanticObjectId
    user_id: PydanticObjectId
    status: JoinRequestStatus = JoinRequestStatus.PENDING

    class Settings:
        name = "group_join_requests"
        indexes = [("group_id", "user_id")]
