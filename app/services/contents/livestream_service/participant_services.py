from beanie import PydanticObjectId

from app.crud.content.livestream_cruds.participant_crud import participant_crud
from app.models import ParticipantRole, LiveStreamParticipant


class ParticipantService:

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

participant_service = ParticipantService()
