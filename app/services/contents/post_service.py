from beanie import PydanticObjectId

from app.core.response.exceptions import Exceptions
from app.crud.content.post_crud import zawiya_post_crud, group_post_crud
from app.models import ContentType, VisibilityStatus


class PostService:

    @staticmethod
    async def create_post_for_content(
        *,
        user_id: PydanticObjectId,
        content_id: PydanticObjectId,
        content_type: ContentType,
        zawiya_id: PydanticObjectId | None = None,
        group_id: PydanticObjectId | None = None,
        visibility: VisibilityStatus = VisibilityStatus.PUBLIC,
    ):
        # 🔐 Target already validated before calling this
        if zawiya_id:
            return await zawiya_post_crud.create(
                user_id=user_id,
                zawiya_id=zawiya_id,
                content_id=content_id,
                content_type=content_type,
                visibility=visibility,
                published=True,
            )

        if group_id:
            return await group_post_crud.create(
                user_id=user_id,
                group_id=group_id,
                content_id=content_id,
                content_type=content_type,
                visibility=VisibilityStatus.GROUP,
                published=True,
            )

        raise Exceptions.bad_request(detail="Invalid post target")
