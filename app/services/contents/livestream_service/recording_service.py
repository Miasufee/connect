from beanie import PydanticObjectId

from app.crud.livestream_cruds.recording_crud import recording_crud
from app.models import RecordingStatus, Recording


class RecordingService:
    # --------------------- Recording ---------------------
    @staticmethod
    async def create_recording(stream_id: PydanticObjectId, storage_path: str, _format="mp4") -> Recording:
        """Start a recording entry."""
        return await recording_crud.create(
            stream_id=stream_id,
            storage_path=storage_path,
            format=_format,
            status=RecordingStatus.PENDING
        )

recording_service = RecordingService()