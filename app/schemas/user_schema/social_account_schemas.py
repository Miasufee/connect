from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.enums import SocialProvider


class SocialAccountBase(BaseModel):
    provider: SocialProvider
    provider_user_id: str = Field(..., max_length=255)


class SocialAccountCreate(SocialAccountBase):
    user_id: int
    access_token: str = Field(..., max_length=512)


class SocialAccountUpdate(BaseModel):
    access_token: Optional[str] = Field(None, max_length=512)


class SocialAccountResponse(SocialAccountBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    # Note: access_token is intentionally excluded from response for security
