from enum import Enum
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel, ASCENDING

from app.models.models_base import TimestampMixin, SoftDeleteMixin


# --------------------- ROLES ---------------------
class ZawiyaRoles(str, Enum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    MODERATOR = "Moderator"

class NotificationLevel(str, Enum):
    ALL = "all"
    PERSONALIZED = "personalized"
    NONE = "none"


# --------------------- MAIN CHANNEL ---------------------
class Zawiya(Document, TimestampMixin, SoftDeleteMixin):
    """Zawiya document — works like a channel."""
    title: str = Field(..., min_length=3, max_length=150)
    name: str = Field(..., min_length=3, max_length=150)
    description: Optional[str] = Field(default="", min_length=10)
    is_verified: bool = False

    owner_id: PydanticObjectId
    verified_by: Optional[PydanticObjectId] = None

    class Settings:
        name = "zawiya"
        indexes = [
            "title",
            "name",
            "is_verified",
            "owner_id",
            "verified_by",
        ]


# --------------------- PROFILE ---------------------
class ZawiyaProfile(Document, TimestampMixin, SoftDeleteMixin):
    zawiya_id: PydanticObjectId
    avatar: Optional[str] = None
    banner: Optional[str] = None
    sheik_name: Optional[str] = None

    class Settings:
        name = "zawiya_profile"
        indexes = [
            IndexModel(
                [("zawiya_id", ASCENDING)],
                unique=True
            )
        ]


# --------------------- ADDRESS ---------------------
class ZawiyaAddress(Document, TimestampMixin, SoftDeleteMixin):
    zawiya_id: PydanticObjectId
    country: str = Field(..., min_length=3, max_length=255)
    state: str = Field(..., min_length=3, max_length=255)
    city: str = Field(..., min_length=3, max_length=255)
    address: str = Field(..., min_length=10, max_length=1000)
    postal_code: str = Field(..., min_length=3)

    latitude: float = Field(...)
    longitude: float = Field(...)

    class Settings:
        name = "zawiya_address"


# --------------------- ANALYTICS ---------------------
class ZawiyaAnalytics(Document, TimestampMixin):
    zawiya_id: PydanticObjectId

    total_videos: int = 0
    total_likes: int = 0
    total_subscribers: int = 0
    total_livestreams: int = 0
    total_content: int = 0

    class Settings:
        name = "zawiya_analytics"


# --------------------- SUBSCRIPTIONS ---------------------
class ZawiyaSubscription(Document, TimestampMixin, SoftDeleteMixin):
    user_id: PydanticObjectId
    zawiya_id: PydanticObjectId

    notification_level: NotificationLevel = NotificationLevel.PERSONALIZED

    class Settings:
        name = "zawiya_subscriptions"
        indexes = [
            IndexModel(
                [("user_id", 1), ("zawiya_id", 1)],
                unique=True
            )
        ]


# --------------------- ADMINS ---------------------
class ZawiyaAdmin(Document, TimestampMixin, SoftDeleteMixin):
    user_id: PydanticObjectId
    zawiya_id: PydanticObjectId
    role: ZawiyaRoles = ZawiyaRoles.ADMIN

    class Settings:
        name = "zawiya_admins"
        indexes = [("user_id", "zawiya_id")]