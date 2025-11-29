from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class ZawiyaAddress(BaseModel):
    zawiya_id: PydanticObjectId

class ZawiyaAddressCreate(ZawiyaAddress):
    country: str = Field(..., min_length=3, max_length=255)
    state: str = Field(..., min_length=3, max_length=255)
    city: str = Field(..., min_length=3, max_length=255)
    address: str = Field(..., min_length=10, max_length=1000)
    postal_code: str = Field(..., min_length=3)

    latitude: float = Field(...)
    longitude: float = Field(...)