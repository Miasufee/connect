from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel


class Zawiya(BaseModel):
    title: str
    name: str

class ZawiyaCreate(Zawiya):
    description: Optional[str] = None
    owner_id: PydanticObjectId

class ZawiyaVerify(BaseModel):
    zawiya_id: PydanticObjectId

class ZawiyaUpdate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[PydanticObjectId] = None