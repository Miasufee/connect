from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field, EmailStr, BaseModel
from enum import Enum

from app.models.models_base import TimestampMixin


# ------------------------------
# Enums
# ------------------------------

class Role(str, Enum):
    """User roles."""
    admin = "admin"
    super_admin = "superadmin"
    superuser = "superuser"

# ------------------------------
# Main User Document
# ------------------------------

class AuthMixin(BaseModel):
    token_version: int = 1
    last_login_at: Optional[datetime] = None

class EmailMixin(AuthMixin):
    email: EmailStr

class User(Document, TimestampMixin, EmailMixin):
    """Main user document."""
    user_role: str = "User"
    is_active: bool = True
    is_email_verified: bool = False
    google_user_id: Optional[str] = None
    email_verified_at: Optional[datetime] = None

    class Settings:
        name = "users"
        indexes = [
            "email",
            "user_role",
            "is_email_verified"
        ]


class Admins(Document, TimestampMixin, EmailMixin):
    """Admins and superusers."""
    role: Role = Role.admin
    hashed_password: str = Field(min_length=1)
    unique_id: str = Field(min_length=1)

    class Settings:
        name = "admins"
        indexes = ["email", "unique_id", "role", "is_active"]

# ------------------------------
# UserProfile
# ------------------------------

class UserProfile(Document, TimestampMixin):
    """User profile info."""
    user_id: str = Field(..., min_length=1)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=512)
    bio: Optional[str] = Field(None, max_length=500)
    date_of_birth: Optional[datetime] = None

    class Settings:
        name = "user_profiles"
        indexes = ["user_id"]


# ------------------------------
# PhoneNumber
# ------------------------------

class PhoneNumber(Document, TimestampMixin):
    """Phone number structure."""
    user_id: str = Field(..., min_length=1)
    country_code: str = Field(..., max_length=4)
    phone_number: str = Field(..., max_length=20)
    is_verified: bool = False
    is_primary: bool = False
    verified_at: Optional[datetime] = None

    class Settings:
        name = "phone_numbers"
        indexes = ["user_id", "phone_number"]


# ------------------------------
# UserPreferences
# ------------------------------

class UserPreferences(Document, TimestampMixin):
    """User preferences and settings."""
    user_id: str = Field(..., min_length=1)
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    language: str = Field(default="en", max_length=5)
    timezone: str = "UTC"
    theme: str = Field(default="light", pattern="^(light|dark|auto)$")

    class Settings:
        name = "user_preferences"
        indexes = ["user_id"]


# ------------------------------
# Verification Codes
# ------------------------------

class VerificationCode(Document, TimestampMixin):
    """Email/Phone/Password/2FA verification codes."""
    user_id: str = Field(..., min_length=1)
    code: str = Field(..., max_length=6)
    expires_at: datetime

    class Settings:
        name = "verification_codes"
        indexes = [
            "user_id",
            "expires_at",
            [("created_at", 1)],
        ]


# ------------------------------
# Refresh Tokens
# ------------------------------

class RefreshedToken(Document, TimestampMixin):
    """Refresh tokens for JWT rotation."""
    user_id: str = Field(..., min_length=1)
    refresh_token: str = Field(..., max_length=510)
    expires_at: datetime
    revoked: bool = False
    revoked_at: Optional[datetime] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

    class Settings:
        name = "refreshed_tokens"
        indexes = [
            "user_id",
            "refresh_token",
            "expires_at",
            "revoked",
            [("expires_at", 1), ("revoked", 1)],
            [("user_id", 1), ("created_at", -1)]
        ]
