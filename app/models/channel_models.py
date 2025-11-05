from datetime import datetime
from typing import List, Optional, Dict
from beanie import Document, Indexed, Link
from pydantic import Field
from enum import Enum
from .user_models import User


# ------------------------------
# Helper function for UTC now
# ------------------------------

def utc_now():
    """Return timezone-aware UTC datetime"""
    return datetime.now().astimezone()


# ------------------------------
# Enums for Choices
# ------------------------------


class ChannelRole(str, Enum):
    owner = "owner"
    admin = "admin"
    moderator = "moderator"


class SubscriptionStatus(str, Enum):
    active = "active"
    cancelled = "cancelled"
    expired = "expired"


class SubscriptionTier(str, Enum):
    free = "free"
    premium = "premium"
    vip = "vip"

# ------------------------------
# Channel Documents
# ------------------------------

class Channel(Document):
    channel_title: str = Field(..., min_length=3, max_length=255)
    channel_name: Indexed(str, unique=True)
    channel_description: Optional[str] = Field("", max_length=1000)
    channel_avatar: Optional[str] = None
    channel_banner: Optional[str] = None

    is_verified: bool = False
    is_active: bool = True
    is_public: bool = True

    channel_owner: Link[User]
    admins: List[Link["ChannelAdmin"]] = []

    subscriber_count: int = 0
    video_count: int = 0
    total_views: int = 0

    website_url: Optional[str] = None
    social_links: Dict[str, str] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "channels"

    async def save(self, *args, **kwargs):
        self.updated_at = utc_now()
        return await super().save(*args, **kwargs)


class ChannelAdmin(Document):
    user: Link[User]
    channel: Link[Channel]
    role: ChannelRole = ChannelRole.admin
    permissions: List[str] = Field(default_factory=lambda: ["view_analytics"])
    assigned_by: Optional[Link[User]] = None

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    class Settings:
        name = "channel_admins"

    async def save(self, *args, **kwargs):
        self.updated_at = utc_now()
        return await super().save(*args, **kwargs)


class ChannelSubscription(Document):
    user: Link[User]
    channel: Link[Channel]

    status: SubscriptionStatus = SubscriptionStatus.active
    tier: SubscriptionTier = SubscriptionTier.free

    subscribed_at: datetime = Field(default_factory=utc_now)
    cancelled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    receive_notifications: bool = True
    email_notifications: bool = False

    class Settings:
        name = "channel_subscriptions"
