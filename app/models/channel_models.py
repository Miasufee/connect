from typing import List, Optional
from beanie import Document, Link, PydanticObjectId
from pydantic import Field
from enum import Enum

from .models_base import utc_now, TimestampMixin
from .user_models import User

# ------------------------------
# Enums for Choices
# ------------------------------

class ChannelRole(str, Enum):
    owner = "owner"
    admin = "admin"
    moderator = "moderator"

class ChannelNotificationLevel(str, Enum):
    all = ""
# ------------------------------
# Channel Documents
# ------------------------------

class Channel(Document, TimestampMixin):
    channel_title: str = Field(..., min_length=3, max_length=255)
    channel_name: str = Field(..., min_length=3, max_length=255)
    channel_description: Optional[str] = Field("", max_length=1000)
    channel_avatar: Optional[str] = None
    channel_banner: Optional[str] = None

    is_verified: bool = False
    is_active: bool = True
    is_public: bool = True

    channel_owner: PydanticObjectId
    admins: List[PydanticObjectId["ChannelAdmin"]] = []

    subscriber_count: int = 0
    video_count: int = 0
    total_views: int = 0


    class Settings:
        name = "channels"

class ChannelAdmin(Document, TimestampMixin):
    user: PydanticObjectId
    channel: PydanticObjectId
    role: ChannelRole = ChannelRole.admin
    permissions: List[str] = Field(default_factory=lambda: ["view_analytics"])
    assigned_by: Optional[PydanticObjectId[User]] = None


    class Settings:
        name = "channel_admins"


class ChannelSubscription(Document, TimestampMixin):
    user: PydanticObjectId
    channel: PydanticObjectId


    class Settings:
        name = "channel_subscriptions"
