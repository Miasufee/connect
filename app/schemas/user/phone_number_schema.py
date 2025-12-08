from datetime import datetime
from typing import Optional
import re

from pydantic import BaseModel, Field, field_validator
from beanie import PydanticObjectId


class PhoneNumberBase(BaseModel):
    country_code: str
    phone_number: str

    @field_validator('country_code')
    def validate_country_code(cls, v):
        v = v.strip()
        if not v.startswith('+'):
            v = f'+{v}'
        return v

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        v = re.sub(r'[\s\-\(\)]', '', v)
        return v


class PhoneNumberCreate(PhoneNumberBase):
    user_id: PydanticObjectId
    is_primary: bool = False


class PhoneNumberUpdate(BaseModel):
    country_code: Optional[str] = None
    phone_number: Optional[str] = None
    is_primary: Optional[bool] = None


class PhoneNumberResponse(PhoneNumberBase):
    id: PydanticObjectId = Field(alias="_id")
    user_id: PydanticObjectId
    is_verified: bool
    is_primary: bool
    verified_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
