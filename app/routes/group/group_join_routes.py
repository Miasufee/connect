from beanie import PydanticObjectId
from fastapi import APIRouter

from app.core.utils.dependencies import RegularUser
from app.models import JoinRequestStatus
from app.services.group_services.group_join_request_service import GroupJoinRequestService

group_join_router = APIRouter(prefix="/group/request", tags=["group-request"])


@group_join_router.post("/")
async def request_join(
        group_id: PydanticObjectId,
        user_id: RegularUser = None
):
    return await GroupJoinRequestService.request_join(
        group_id=group_id,
        user_id=user_id.id
    )

@group_join_router.put("/approve")
async def request_join_approve(
        group_id: PydanticObjectId,
        status: JoinRequestStatus,
        user_id: RegularUser = None,

):
    return await GroupJoinRequestService.approve(
        group_id=group_id,
        user_id=user_id.id,
        status=status
    )

@group_join_router.get("/get")
async def get_request_list(
        group_id: PydanticObjectId,
        user_id: RegularUser = None,
        page: int = 1,
        per_page: int = 30
):
    return await GroupJoinRequestService.get_join_requests(
        group_id=group_id,
        user_id=user_id.id,
        page=page,
        per_page=per_page
    )

@group_join_router.get("/joined")
async def get_joined_request_list(
        group_id: PydanticObjectId,
        user_id: RegularUser = None,
        page: int = 1,
        per_page: int = 30
):
    return await GroupJoinRequestService.get_joined_requests(
        group_id=group_id,
        user_id=user_id.id,
        page=page,
        per_page=per_page
    )

