from typing import Optional

from beanie import before_event, Insert, Replace, SaveChanges, PydanticObjectId
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class SoftDeleteMixin(BaseModel):
    """
    Provides soft deletion functionality for Beanie documents.
    Instead of deleting, marks the document as deleted and records the time.
    """

    is_deleted: bool = Field(default=False, description="Whether the document is soft deleted")
    deleted_at: datetime | None = Field(default=None, description="Timestamp when the document was deleted")

    async def soft_delete(self):
        """
        Mark this document as deleted instead of removing it from the DB.
        Updates 'is_deleted' and 'deleted_at' fields.
        """
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        await self.save()

    async def restore(self):
        """
        Restore a soft-deleted document.
        """
        self.is_deleted = False
        self.deleted_at = None
        await self.save()

    async def hard_delete(self):
        """
        Permanently remove the document from the database.
        Use with caution.
        """
        await self.delete()



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

class TitleMixin(BaseModel):
    """ title mixin """
    title: str = Field(..., min_length=3, max_length=255)

class DescriptionMixin(BaseModel):
    """ description mixin"""
    description: Optional[str] = Field(default="", min_length=10)

class UserIdMixin(BaseModel):
    """ User id mixin """
    user_id: PydanticObjectId

class ZawiyaIdMixin(BaseModel):
    """ Zawiya id Mixin"""
    zawiya_id: PydanticObjectId

def utc_now():
    return datetime.now(timezone.utc)

