from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserLogin(UserBase):
    verification_code: Optional[str] = None

class VerificationCode(UserLogin):
    pass

class UserResponse(UserBase):
    user_role: Optional[str] = None
    is_email_verify: bool = False
    # unique_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
