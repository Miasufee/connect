from beanie import PydanticObjectId

from app.core.response.exceptions import Exceptions
from app.crud.group_cruds.group_join_requst_crud import group_join_request_crud
from app.crud.group_cruds.group_member_crud import group_member_crud
from app.models import JoinRequestStatus
from app.models.group_models import GroupJoinRequest
from app.services.group_services.group_policy import GroupPolicy


class GroupJoinRequestService:
    @staticmethod
    async def request_join(group_id: PydanticObjectId, user_id: PydanticObjectId):
        return await group_join_request_crud.create(
            group_id=group_id,
            user_id=user_id,
        )

    @staticmethod
    async def approve(
            group_id: PydanticObjectId,
            user_id: PydanticObjectId,
            status: JoinRequestStatus
    ):
        is_admin = await GroupPolicy.is_group_admin(
            group_id=group_id,
            user_id=user_id
        )
        if not is_admin:
            raise Exceptions.forbidden(detail="Your not group")

        join_request = await group_join_request_crud.update_by_filter(
            filters={
                "group_id": group_id,
                "user_id": user_id,
                "status": status.PENDING
            },
            update_data={
                "status": status.APPROVED
            }
        )
        await group_member_crud.add_member(
            group_id=join_request.group_id,
            user_id=join_request.user_id,
        )

    @staticmethod
    async def get_join_requests(
            group_id: PydanticObjectId,
            user_id: PydanticObjectId,
            page: int = 1,
            per_page: int = 30
    ):

        is_admin = await GroupPolicy.is_group_admin(
            group_id=group_id,
            user_id=user_id
        )
        if not is_admin:
            raise Exceptions.forbidden(detail="Your not group")

        return await group_join_request_crud.paginate(
            page=page,
            per_page=per_page,
            filters={
                "group_id": group_id,
                "status": JoinRequestStatus.PENDING
            }
        )

    @staticmethod
    async def get_joined_requests(
            group_id: PydanticObjectId,
            user_id: PydanticObjectId,
            page: int = 1,
            per_page: int = 30
    ):

        is_admin = await GroupPolicy.is_group_admin(
            group_id=group_id,
            user_id=user_id
        )
        if not is_admin:
            raise Exceptions.forbidden(detail="Your not group")

        return await group_join_request_crud.paginate(
            page=page,
            per_page=per_page,
            filters={
                "group_id": group_id,
                "status": JoinRequestStatus.APPROVED
            }
        )
