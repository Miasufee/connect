from beanie import PydanticObjectId
from pydantic import BaseModel

from app.models.zawiya_models import ZawiyaRoles


class ZawiyaAdmin(BaseModel):
    zawiya_id: PydanticObjectId

class ZawiyaAdminCreate(BaseModel):
    user_id: PydanticObjectId
    zawiya_id: PydanticObjectId
    role: ZawiyaRoles

class ZawiyaRoleUpdate(BaseModel):
    admin_id: PydanticObjectId
    zawiya_id: PydanticObjectId
    role: ZawiyaRoles

class AdminRemove(BaseModel):
    admin_id: PydanticObjectId
    zawiya_id: PydanticObjectId