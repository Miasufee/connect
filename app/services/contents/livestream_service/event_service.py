from typing import Optional

from beanie import PydanticObjectId

from app.crud.livestream_cruds.livestream_event_crud import event_crud


class EventSrvice:
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
