from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from beanie import PydanticObjectId


class UserProfileBase(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=512)
    bio: Optional[str] = Field(None, max_length=500)
    date_of_birth: Optional[datetime] = None

    @field_validator('first_name', 'last_name', 'bio')
    def validate_fields(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class UserProfileCreate(UserProfileBase):
    user_id: PydanticObjectId


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileResponse(UserProfileBase):
    id: PydanticObjectId = Field(alias="_id")
    user_id: PydanticObjectId
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
