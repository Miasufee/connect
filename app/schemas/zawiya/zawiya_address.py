from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class ZawiyaAddress(BaseModel):
    zawiya_id: PydanticObjectId

class ZawiyaAddressCreate(ZawiyaAddress):
    country: Optional[str] = Field(None, min_length=3, max_length=255)
    state: Optional[str] = Field(None, min_length=3, max_length=255)
    city: Optional[str] = Field(None, min_length=3, max_length=255)
    address: Optional[str] = Field(None, min_length=10, max_length=1000)
    postal_code: Optional[str] = Field(None, min_length=3)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
