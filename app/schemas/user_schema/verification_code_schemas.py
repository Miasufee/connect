from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional
from datetime import datetime


class VerificationCodeBase(BaseModel):
    code: str = Field(..., min_length=4, max_length=6, description="Verification code")
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isdigit():
            raise ValueError('Verification code must contain only digits')
        return v


class VerificationCodeCreate(VerificationCodeBase):
    user_id: int
    expired_at: datetime


class VerificationCodeVerify(BaseModel):
    user_id: int
    code: str = Field(..., min_length=4, max_length=6)


class VerificationCodeResponse(VerificationCodeBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    expired_at: datetime
    created_at: datetime
    updated_at: datetime
    
    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expired_at.replace(tzinfo=None)
