from beanie import PydanticObjectId

from app.crud.content.video_crud import video_crud
from app.models import VideoStatus, ContentType
from app.services.contents.content_base_service import BaseContentService
from app.services.contents.post_service import PostService


class VideoService(BaseContentService):

    @classmethod
    async def create_video(
        cls,
        *,
        user_id: PydanticObjectId,
        title: str,
        description: str | None = None,
        zawiya_id: PydanticObjectId | None = None,
        group_id: PydanticObjectId | None = None,
    ):

        await cls.validate_target(
            zawiya_id=zawiya_id,
            group_id=group_id,
        )

        await cls.check_permissions(
            zawiya_id=zawiya_id,
            group_id=group_id,
            user_id=user_id,
        )

        new_video = await video_crud.create(
            user_id=user_id,
            zawiya_id=zawiya_id,
            group_id=group_id,
            title=title,
            description=description,
            status=VideoStatus.UPLOADED,
        )

        post = await PostService.create_post_for_content(
            user_id=user_id,
            content_id=new_video.id,
            content_type=ContentType.VIDEO,
            zawiya_id=zawiya_id,
            group_id=group_id,
        )
        return post

    @staticmethod
    async def update_video():
        pass

    @staticmethod
    async def delete_video():
        pass