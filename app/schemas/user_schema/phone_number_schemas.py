from pydantic import BaseModel, Field, ConfigDict, validator
from typing import Optional
from datetime import datetime
import re


class PhoneNumberBase(BaseModel):
    country_code: str = Field(..., max_length=4, description="Country code with + prefix")
    phone_number: str = Field(..., max_length=20, description="Phone number without country code")
    is_verified: bool = False
    
    @validator('country_code')
    def validate_country_code(cls, v):
        if not v.startswith('+'):
            raise ValueError('Country code must start with +')
        if not v[1:].isdigit():
            raise ValueError('Country code must contain only digits after +')
        return v
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Remove any non-digit characters for validation
        digits_only = re.sub(r'\D', '', v)
        if len(digits_only) < 7 or len(digits_only) > 15:
            raise ValueError('Phone number must be between 7 and 15 digits')
        return v


class PhoneNumberCreate(PhoneNumberBase):
    user_id: int


class PhoneNumberUpdate(BaseModel):
    country_code: Optional[str] = Field(None, max_length=4)
    phone_number: Optional[str] = Field(None, max_length=20)
    is_verified: Optional[bool] = None
    
    @validator('country_code')
    def validate_country_code(cls, v):
        if v is not None:
            if not v.startswith('+'):
                raise ValueError('Country code must start with +')
            if not v[1:].isdigit():
                raise ValueError('Country code must contain only digits after +')
        return v


class PhoneNumberResponse(PhoneNumberBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    @property
    def full_number(self) -> str:
        return f"{self.country_code}{self.phone_number}"
