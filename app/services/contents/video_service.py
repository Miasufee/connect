from beanie import PydanticObjectId

from app.core.response.exceptions import Exceptions
from app.services.zawiya.zawiya_permissions import zawiya_permission


class VideoService:
    def __init__(self):
        pass

    @staticmethod
    async def _create_video(
            zawiya_id: PydanticObjectId,
            group_id: PydanticObjectId | None,
            user_id: PydanticObjectId,
            title: str,
            description: str | None
    ):
        is_owner = await zawiya_permission.require_admin_or_owner(
            zawiya_id=zawiya_id,
            user_id=user_id
        )
        if not is_owner:
            raise Exceptions.forbidden(detail="Your not and admin")