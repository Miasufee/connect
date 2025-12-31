from beanie import PydanticObjectId
from datetime import datetime
from typing import  Optional
from app.crud import (
    live_stream_crud,
    participant_crud,
    webrtc_session_crud,
    webrtc_peer_crud,
    recording_crud,
    analytics_crud,
    event_crud,
)
from app.models import (
    LiveStream,
    LiveStreamParticipant,
    WebRTCSession,
    WebRTCPeer,
    Recording,
    StreamStatus,
    ParticipantRole,
    LiveStreamEvent, RecordingStatus,
)


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
        return await live_stream_crud.update(stream_id, {"status": StreamStatus.LIVE, "started_at": datetime.utcnow()})

    @staticmethod
    async def end_stream(stream_id: PydanticObjectId):
        """Set stream as ENDED and record end time."""
        return await live_stream_crud.update(stream_id, {"status": StreamStatus.ENDED, "ended_at": datetime.utcnow()})


    # --------------------- Participants ---------------------
    @staticmethod
    async def add_participant(
        stream_id: PydanticObjectId,
        user_id: PydanticObjectId,
        role: ParticipantRole = ParticipantRole.VIEWER,
        can_publish_audio=False,
        can_publish_video=False,
        can_share_screen=False,
    ) -> LiveStreamParticipant:
        """Add participant to a live stream with permissions."""
        return await participant_crud.create(
            stream_id=stream_id,
            user_id=user_id,
            role=role,
            can_publish_audio=can_publish_audio,
            can_publish_video=can_publish_video,
            can_share_screen=can_share_screen,
        )

    @staticmethod
    async def remove_participant(stream_id: PydanticObjectId, user_id: PydanticObjectId):
        """Remove participant from stream."""
        await participant_crud.delete_by_filter(stream_id=stream_id, user_id=user_id)

    @staticmethod
    async def promote_participant(stream_id: PydanticObjectId, user_id: PydanticObjectId, role: ParticipantRole):
        """Promote or change participant role (e.g., viewer → co-host)."""
        participant = await participant_crud.get_one(stream_id=stream_id, user_id=user_id)
        if participant:
            participant.role = role
            if role in [ParticipantRole.OWNER, ParticipantRole.CO_HOST]:
                participant.can_publish_audio = True
                participant.can_publish_video = True
                participant.can_share_screen = True
            await participant.save()
            return participant
        return None

    @staticmethod
    async def mute_participant(stream_id: PydanticObjectId, user_id: PydanticObjectId):
        participant = await participant_crud.get_one(stream_id=stream_id, user_id=user_id)
        if participant:
            participant.is_muted = True
            await participant.save()
            return participant
        return None

    @staticmethod
    async def unmute_participant(stream_id: PydanticObjectId, user_id: PydanticObjectId):
        participant = await participant_crud.get_one(stream_id=stream_id, user_id=user_id)
        if participant:
            participant.is_muted = False
            await participant.save()
            return participant
        return None

    @staticmethod
    async def ban_participant(stream_id: PydanticObjectId, user_id: PydanticObjectId):
        participant = await participant_crud.get_one(stream_id=stream_id, user_id=user_id)
        if participant:
            participant.is_banned = True
            await participant.save()
            return participant
        return None

    @staticmethod
    async def unban_participant(stream_id: PydanticObjectId, user_id: PydanticObjectId):
        participant = await participant_crud.get_one(stream_id=stream_id, user_id=user_id)
        if participant:
            participant.is_banned = False
            await participant.save()
            return participant
        return None


    # --------------------- WebRTC Sessions ---------------------
    @staticmethod
    async def create_webrtc_session(stream_id: PydanticObjectId, sfu_type: str, sfu_room_id: str) -> WebRTCSession:
        """Create a WebRTC session for the SFU."""
        return await webrtc_session_crud.create(stream_id=stream_id, sfu_type=sfu_type, sfu_room_id=sfu_room_id)

    @staticmethod
    async def add_webrtc_peer(session_id: PydanticObjectId, user_id: PydanticObjectId, peer_id: str) -> WebRTCPeer:
        """Register a new peer in the WebRTC session."""
        return await webrtc_peer_crud.create(session_id=session_id, user_id=user_id, peer_id=peer_id)


    # --------------------- Recording ---------------------
    @staticmethod
    async def create_recording(stream_id: PydanticObjectId, storage_path: str, format="mp4") -> Recording:
        """Start a recording entry."""
        return await recording_crud.create(
            stream_id=stream_id,
            storage_path=storage_path,
            format=format,
            status=RecordingStatus.PENDING
        )


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


    # --------------------- Events / Moderation ---------------------
    @staticmethod
    async def log_event(
        stream_id: PydanticObjectId,
        actor_id: PydanticObjectId,
        event_type: str,
        target_id: Optional[PydanticObjectId] = None,
        reason: Optional[str] = None
    ):
        """Log moderation or action event."""
        return await event_crud.create(
            stream_id=stream_id,
            actor_id=actor_id,
            target_id=target_id,
            event_type=event_type,
            reason=reason
        )


    # --------------------- Fetch Active Streams ---------------------
    @staticmethod
    async def get_active_streams(zawiya_id: Optional[PydanticObjectId] = None):
        """Return streams that are LIVE or CREATED (not ended)."""
        filters = {"status": {"$in": [StreamStatus.CREATED, StreamStatus.LIVE]}}
        if zawiya_id:
            filters["zawiya_id"] = zawiya_id
        return await live_stream_crud.get_multi(filters=filters)
