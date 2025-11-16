from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


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

class PasswordResetRequest(BaseModel):
    unique_id: str
    email: EmailStr


class PasswordResetValidate(BaseModel):
    email: EmailStr
    token: str


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class PasswordResetResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None