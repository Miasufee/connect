from beanie import PydanticObjectId
from fastapi import UploadFile

from app.core.response.exceptions import Exceptions
from app.core.response.success import Success
from app.core.storage.media import save_image
from app.crud.group_cruds.group_profile_crud import group_profile_crud
from app.services.group_services.group_policy import GroupPolicy


class GroupProfileService:
    @staticmethod
    async def set_group_profile(
            group_id: PydanticObjectId,
            user_id: PydanticObjectId,
            avatar: UploadFile | None = None,
    ):
        is_owner = await GroupPolicy.is_group_admin(
            group_id=group_id,
            user_id=user_id
        )
        if not is_owner:
            raise Exceptions.forbidden(detail="Your Can Perform Such Action")
        avatar_path = None

        if avatar:
            avatar_path = await save_image(avatar)

        await group_profile_crud.set_profile(
            group_id=group_id,
            avatar_url=avatar_path
        )

        return Success.ok(message="Profile Success")

    @staticmethod
    async def get_group_profile(group_id: PydanticObjectId):
        return group_profile_crud.get(group_id)

    @staticmethod
    async def delete_group_profile(group_id: PydanticObjectId, user_id: PydanticObjectId):
        is_owner = await GroupPolicy.is_group_admin(
            group_id=group_id,
            user_id=user_id
        )
        if not is_owner:
            raise Exceptions.forbidden(detail="Your Can Perform Such Action")
        return group_profile_crud.delete(group_id)