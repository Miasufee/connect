from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from beanie import PydanticObjectId
from app.models.user_models import UserRole
from app.schemas.base_schema import UserBase, PaginatedResponse


class UserCreate(UserBase):
    pass

class UserLogin(UserBase):
    verification_code: Optional[str] = None


class VerificationCode(UserLogin):
    pass


class SuperUserLogin(UserBase):
    unique_id: str
    password: str


class PasswordResetRequest(UserBase):
    unique_id: str


class PasswordResetValidate(UserBase):
    token: str


class PasswordResetConfirm(UserBase):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class PasswordResetResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class RoleUpdate(UserBase):
    new_role: UserRole


class UserOut(BaseModel):
    id: PydanticObjectId
    email: EmailStr
    user_role: Optional[str] = None
    is_active: bool
    is_email_verified: bool
    google_user_id: Optional[str] = None
    token_version: Optional[int] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class PaginatedUsers(PaginatedResponse):
    items: List[UserOut]