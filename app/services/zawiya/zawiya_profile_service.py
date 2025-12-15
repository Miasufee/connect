from __future__ import annotations

from beanie import PydanticObjectId
from fastapi import UploadFile, Request

from app.core.response.exceptions import Exceptions
from app.core.storage.media import save_image, media_url
from app.crud.zawiya_cruds import zawiya_profile_crud
from app.crud.zawiya_cruds.zawiya_admin_crud import zawiya_admin_crud
from app.services.zawiya.zawiya_permissions import zawiya_permission


class ZawiyaProfileService:

    async def create_or_update(
        self,
        *,
        zawiya_id: PydanticObjectId,
        user_id: PydanticObjectId,
        avatar: UploadFile | None = None,
        banner: UploadFile | None = None,
        sheik: str | None = None,
    ):
        # # ownership check
        await zawiya_permission.require_admin_or_owner(
            zawiya_id=zawiya_id,
            user_id=user_id,
        )

        avatar_path = None
        banner_path = None

        if avatar:
            avatar_path = await save_image(avatar)

        if banner:
            banner_path = await save_image(banner)

        return await zawiya_profile_crud.create_or_update_profile(
            zawiya_id=zawiya_id,
            avatar=avatar_path,
            banner=banner_path,
            sheik_name=sheik,
        )

    async def get(self, zawiya_id: PydanticObjectId, request: Request):
        profile = await zawiya_profile_crud.get_profile(zawiya_id)
        if not profile:
            raise Exceptions.not_found("Profile not found")

        return {
            "zawiya_id": str(profile.zawiya_id),
            "sheik_name": profile.sheik_name,
            "avatar_url": media_url(profile.avatar),
            "banner_url": media_url(profile.banner),
        }

    async def delete(
        self,
        *,
        zawiya_id: PydanticObjectId,
        user_id: PydanticObjectId,
    ):
        if not await zawiya_admin_crud.is_owner(user_id, zawiya_id):
            raise Exceptions.permission_denied("You are not the owner")

        deleted = await zawiya_profile_crud.delete_zawiya_profile(zawiya_id)
        if not deleted:
            raise Exceptions.not_found("Profile not found")

        return {"deleted": True}


zawiya_profile_service = ZawiyaProfileService()
