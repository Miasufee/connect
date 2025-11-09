from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class User(UserBase):
    pass

class UserCreate(UserBase):
    pass

class UserLogin(UserBase):
    verification_code: Optional[str] = None

class VerificationCode(UserLogin):
    pass

class UserResponse(UserBase):
    user_role: Optional[str] = None
    is_email_verify: bool = False
    created_at: datetime
    updated_at: datetime

class SuperUserLogin(UserBase):
    unique_id: str
    password: str