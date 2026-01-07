from beanie import PydanticObjectId

from app.core.response.exceptions import Exceptions
from app.services.group_services.group_policy import GroupPolicy
from app.services.zawiya.zawiya_permissions import zawiya_permission


class BaseContentService:
    # -----------------------------
    # TARGET VALIDATION
    # -----------------------------
    @staticmethod
    async def validate_target(
        *,
        zawiya_id: PydanticObjectId | None,
        group_id: PydanticObjectId | None,
    ) -> None:
        if zawiya_id and group_id:
            raise Exceptions.bad_request(
                "Content cannot belong to both Zawiya and Group"
            )

        if not zawiya_id and not group_id:
            raise Exceptions.bad_request(
                "Content must belong to either Zawiya or Group"
            )

    # -----------------------------
    # PERMISSION CHECK
    # -----------------------------
    @staticmethod
    async def check_permissions(
        *,
        zawiya_id: PydanticObjectId | None,
        group_id: PydanticObjectId | None,
        user_id: PydanticObjectId,
    ) -> None:

        if zawiya_id:
            await zawiya_permission.require_admin_or_owner(
                zawiya_id=zawiya_id,
                user_id=user_id,
            )

        if group_id:
            if not await GroupPolicy.is_group_admin(group_id, user_id):
                raise Exceptions.forbidden(
                    "Group admin or owner required"
                )
