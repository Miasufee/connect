from beanie import PydanticObjectId

from app.crud.content.livestream_cruds.livestream_anaytics_crud import analytics_crud


class AnalyticsService:

    # --------------------- Analytics ---------------------
    @staticmethod
    async def increment_viewers(stream_id: PydanticObjectId, count: int = 1):
        """Increment viewers count in analytics."""
        analytics = await analytics_crud.get_one({"stream_id": stream_id})
        if analytics:
            analytics.viewers += count
            await analytics.save()
        else:
            await analytics_crud.create(stream_id=stream_id, viewers=count)

    @staticmethod
    async def add_like(stream_id: PydanticObjectId, count: int = 1):
        """Increment likes count in analytics."""
        analytics = await analytics_crud.get_one({"stream_id": stream_id})
        if analytics:
            analytics.likes += count
            await analytics.save()
        else:
            await analytics_crud.create(stream_id=stream_id, likes=count)

analytics_service = AnalyticsService()