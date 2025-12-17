from beanie import PydanticObjectId

from app.crud.zawiya_cruds import zawiya_analytics_crud
from app.models.zawiya_models import ZawiyaAnalytics
from app.core.response.exceptions import Exceptions


class ZawiyaAnalyticsService:
    """Service layer for managing Zawiya analytics."""

    @staticmethod
    async def get_or_create_analytics(zawiya_id: PydanticObjectId) -> ZawiyaAnalytics:
        """Get existing analytics or create new if none exists."""
        return await zawiya_analytics_crud.get_or_create(zawiya_id)

    async def increment_field(
        self,
        zawiya_id: PydanticObjectId,
        field: str,
        amount: int = 1
    ) -> dict:
        """
        Increment a specific field in analytics by a given amount.
        Raises exception if field does not exist.
        """
        analytics = await self.get_or_create_analytics(zawiya_id)
        if not hasattr(analytics, field):
            raise Exceptions.bad_request(f"Field '{field}' does not exist in analytics")
        current_value = getattr(analytics, field)
        setattr(analytics, field, current_value + amount)
        updated = await analytics.save()
        return {
            "success": True,
            "zawiya_id": str(zawiya_id),
            "updated_field": field,
            "new_value": getattr(updated, field),
            "message": f"{field} incremented by {amount}"
        }

    # Convenience methods
    async def add_video(self, zawiya_id: PydanticObjectId) -> dict:
        return await self.increment_field(zawiya_id, "total_videos")

    async def add_like(self, zawiya_id: PydanticObjectId) -> dict:
        return await self.increment_field(zawiya_id, "total_likes")

    async def add_subscriber(self, zawiya_id: PydanticObjectId) -> dict:
        return await self.increment_field(zawiya_id, "total_subscribers")

    async def add_livestream(self, zawiya_id: PydanticObjectId) -> dict:
        return await self.increment_field(zawiya_id, "total_livestreams")

    async def add_content(self, zawiya_id: PydanticObjectId) -> dict:
        return await self.increment_field(zawiya_id, "total_content")

    async def get_analytics(self, zawiya_id: PydanticObjectId) -> ZawiyaAnalytics:
        """Fetch analytics for a Zawiya."""
        return await self.get_or_create_analytics(zawiya_id)


# Singleton instance for internal use
zawiya_analytics_service = ZawiyaAnalyticsService()
