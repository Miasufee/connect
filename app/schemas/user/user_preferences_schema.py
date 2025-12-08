from datetime import datetime
from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, Field, field_validator
import re


class UserPreferencesBase(BaseModel):
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    language: str = "en"
    timezone: str = "UTC"
    theme: str = "light"


class UserPreferencesCreate(UserPreferencesBase):
    user_id: PydanticObjectId


class UserPreferencesUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    theme: Optional[str] = None


class UserPreferencesResponse(UserPreferencesBase):
    id: PydanticObjectId = Field(alias="_id")
    user_id: PydanticObjectId
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
