from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class RefreshTokenBase(BaseModel):
    refresh_token: str = Field(..., max_length=510)
    expired_at: datetime


class RefreshTokenCreate(RefreshTokenBase):
    user_id: int


class RefreshTokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    expired_at: datetime
    created_at: datetime
    updated_at: datetime
    # Note: refresh_token is intentionally excluded from response for security
    
    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expired_at.replace(tzinfo=None)


class RefreshTokenVerify(BaseModel):
    refresh_token: str = Field(..., max_length=510)
