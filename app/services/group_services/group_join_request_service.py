from app.crud.group_cruds.group_join_requst_crud import group_join_request_crud
from app.crud.group_cruds.group_member_crud import group_member_crud
from app.models import JoinRequestStatus
from app.models.group_models import GroupJoinRequest


class GroupJoinRequestService:
    @staticmethod
    async def request_join(group_id, user_id):
        return await group_join_request_crud.create(
            group_id=group_id,
            user_id=user_id,
        )

    @staticmethod
    async def approve(request: GroupJoinRequest):
        request.status = JoinRequestStatus.APPROVED
        await request.save()

        await group_member_crud.add_member(
            group_id=request.group_id,
            user_id=request.user_id,
        )
