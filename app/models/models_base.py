from __future__ import annotations

from typing import Optional

from beanie import before_event, Insert, Replace, SaveChanges, PydanticObjectId
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.models.enums import ContentType, VisibilityStatus


class SoftDeleteMixin(BaseModel):
    """
    Provides soft deletion functionality for Beanie documents.
    Instead of deleting, marks the document as deleted and records the time.
    """

    is_deleted: bool = Field(default=False, description="Whether the document is soft deleted")
    deleted_at: datetime | None = Field(default=None, description="Timestamp when the document was deleted")



class TimestampMixin(BaseModel):
    """
    Adds automatic created_at and updated_at timestamps.
    Automatically updates 'updated_at' before saving or updating.
    """

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @before_event([Insert, Replace, SaveChanges])
    async def update_timestamp(self):
        """Automatically set updated_at before insert, replace, or save"""
        self.updated_at = datetime.now(timezone.utc)

def utc_now():
    return datetime.now(timezone.utc)

class UserIdMixin(BaseModel):
    user_id: PydanticObjectId

class TitleMixin(BaseModel):
    title: str = Field(..., min_length=2, max_length=1000)

class DescriptionMixin(BaseModel):
    description: Optional[str] = None

class ZawiyaIdMixin(BaseModel):
    zawiya_id: PydanticObjectId

class GroupIdMixin(BaseModel):
    group_id: Optional[PydanticObjectId] = None

class PostMixin(BaseModel):

    content_id: PydanticObjectId
    content_type: ContentType
    published: bool = False
    visibility: VisibilityStatus = VisibilityStatus.PRIVATE
    like_count: int = 0
    dislike_count: int = 0
    comment_count: int = 0

