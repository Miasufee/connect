from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel


class ZawiyaProfile(BaseModel):
    zawiya_id: Optional[PydanticObjectId] = None

class ZawiyaProfileCreate(ZawiyaProfile):
    avatar: Optional[str] = None
    banner: Optional[str] = None
    sheik_name: Optional[str] = None