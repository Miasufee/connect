from beanie import PydanticObjectId
from typing import  Optional
from app.crud import live_stream_crud
from app.crud.livestream_cruds.livestream_anaytics_crud import analytics_crud
from app.crud.livestream_cruds.participant_crud import participant_crud
from app.models import LiveStream, StreamStatus, ParticipantRole, utc_now


class LiveStreamService:

    # --------------------- Stream Lifecycle ---------------------
    @staticmethod
    async def create_stream(
        streamer_id: PydanticObjectId,
        zawiya_id: PydanticObjectId,
        title: str,
        description: Optional[str] = None,
        stream_type=LiveStream.stream_type,
        visibility=LiveStream.visibility,
        is_recorded=True,
    ) -> LiveStream:
        """Create a new live stream and add the owner as participant."""
        stream = await live_stream_crud.create(
            streamer_id=streamer_id,
            zawiya_id=zawiya_id,
            title=title,
            description=description,
            stream_type=stream_type,
            visibility=visibility,
            is_recorded=is_recorded,
            status=StreamStatus.CREATED,
        )

        # Add owner as participant with full permissions
        await participant_crud.create(
            stream_id=stream.id,
            user_id=streamer_id,
            role=ParticipantRole.OWNER,
            can_publish_audio=True,
            can_publish_video=True,
            can_share_screen=True,
        )

        # Initialize analytics
        await analytics_crud.create(stream_id=stream.id)

        return stream

    @staticmethod
    async def start_stream(stream_id: PydanticObjectId):
        """Set stream as LIVE and record start time."""
        return await live_stream_crud.update(stream_id, {"status": StreamStatus.LIVE, "started_at": utc_now()})

    @staticmethod
    async def end_stream(stream_id: PydanticObjectId):
        """Set stream as ENDED and record end time."""
        return await live_stream_crud.update(stream_id, {"status": StreamStatus.ENDED, "ended_at": utc_now()})


    # --------------------- Fetch Active Streams ---------------------
    @staticmethod
    async def get_active_streams(zawiya_id: Optional[PydanticObjectId] = None):
        """Return streams that are LIVE or CREATED (not ended)."""
        filters = {"status": {"$in": [StreamStatus.CREATED, StreamStatus.LIVE]}}
        if zawiya_id:
            filters["zawiya_id"] = zawiya_id
        return await live_stream_crud.get_multi(filters=filters)
