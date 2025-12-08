# """
# Pydantic schemas for UserProfile, PhoneNumber, and UserPreferences
# """
# from datetime import datetime
# from typing import Optional, List
# from pydantic import BaseModel, Field, EmailStr, field_validator
# from beanie import PydanticObjectId
# import re
#
#
# from app.models.user_models import UserRole
#
#
# # -------------------------
# # Base
# # -------------------------
#
# class UserBase(BaseModel):
#     email: EmailStr
#
#
# # -------------------------
# # Create / Login / Reset
# # -------------------------
#
# class UserCreate(UserBase):
#     pass
#
#
# class UserLogin(UserBase):
#     verification_code: Optional[str] = None
#
#
# class VerificationCode(UserLogin):
#     pass
#
#
# class SuperUserLogin(UserBase):
#     unique_id: str
#     password: str
#
#
# class PasswordResetRequest(BaseModel):
#     unique_id: str
#     email: EmailStr
#
#
# class PasswordResetValidate(BaseModel):
#     email: EmailStr
#     token: str
#
#
# class PasswordResetConfirm(BaseModel):
#     email: EmailStr
#     token: str
#     new_password: str = Field(..., min_length=8)
#     confirm_password: str = Field(..., min_length=8)
#
#
# class PasswordResetResponse(BaseModel):
#     success: bool
#     message: str
#     data: Optional[dict] = None
#
#
# # -------------------------
# # Role update
# # -------------------------
#
# class RoleUpdate(UserBase):
#     new_role: UserRole
#
#
# # -------------------------
# # Output models
# # -------------------------
#
# class UserOut(BaseModel):
#     id: PydanticObjectId
#     email: EmailStr
#     user_role: Optional[str] = None
#     is_active: bool
#     is_email_verified: bool
#     google_user_id: Optional[str] = None
#     token_version: Optional[int] = None
#     last_login_at: Optional[datetime] = None
#     created_at: datetime
#     updated_at: datetime
#
#     model_config = {
#         "from_attributes": True
#     }
#
#
# # -------------------------
# # Pagination
# # -------------------------
#
# class PaginatedUsers(BaseModel):
#     items: List[UserOut]
#     total: int
#     page: int
#     per_page: int
#     total_pages: int
#     has_next: bool
#     has_prev: bool
#
#
# # ============================================================
# # USER PROFILE SCHEMAS
# # ============================================================
#
# class UserProfileBase(BaseModel):
#     """Base schema for user profile (shared fields)"""
#     first_name: Optional[str] = Field(None, max_length=100, description="User's first name")
#     last_name: Optional[str] = Field(None, max_length=100, description="User's last name")
#     avatar_url: Optional[str] = Field(None, max_length=512, description="Profile avatar URL")
#     bio: Optional[str] = Field(None, max_length=500, description="User biography")
#     date_of_birth: Optional[datetime] = Field(None, description="Date of birth")
#
#     @field_validator('first_name', 'last_name')
#     @classmethod
#     def validate_name(cls, v: Optional[str]) -> Optional[str]:
#         if v is not None:
#             v = v.strip()
#             if not v:
#                 return None
#         return v
#
#     @field_validator('bio')
#     @classmethod
#     def validate_bio(cls, v: Optional[str]) -> Optional[str]:
#         if v is not None:
#             v = v.strip()
#             if not v:
#                 return None
#         return v
#
#
# class UserProfileCreate(UserProfileBase):
#     """Schema for creating user profile"""
#     user_id: PydanticObjectId = Field(..., description="Associated user ID")
#
#
# class UserProfileUpdate(BaseModel):
#     """Schema for updating user profile (all fields optional)"""
#     first_name: Optional[str] = Field(None, max_length=100)
#     last_name: Optional[str] = Field(None, max_length=100)
#     avatar_url: Optional[str] = Field(None, max_length=512)
#     bio: Optional[str] = Field(None, max_length=500)
#     date_of_birth: Optional[datetime] = None
#
#     @field_validator('first_name', 'last_name', 'bio')
#     @classmethod
#     def validate_fields(cls, v: Optional[str]) -> Optional[str]:
#         if v is not None:
#             v = v.strip()
#             if not v:
#                 return None
#         return v
#
#
# class UserProfileResponse(UserProfileBase):
#     """Schema for user profile response"""
#     id: PydanticObjectId = Field(..., alias="_id")
#     user_id: PydanticObjectId
#     created_at: datetime
#     updated_at: datetime
#
#     class Config:
#         populate_by_name = True
#         json_encoders = {
#             PydanticObjectId: str,
#             datetime: lambda v: v.isoformat()
#         }
#
#
# # ============================================================
# # PHONE NUMBER SCHEMAS
# # ============================================================
#
# class PhoneNumberBase(BaseModel):
#     """Base schema for phone number"""
#     country_code: str = Field(..., max_length=4, description="Country calling code (e.g., +234)")
#     phone_number: str = Field(..., max_length=20, description="Phone number without country code")
#
#     @field_validator('country_code')
#     @classmethod
#     def validate_country_code(cls, v: str) -> str:
#         v = v.strip()
#         if not v.startswith('+'):
#             v = f'+{v}'
#         if not re.match(r'^\+\d{1,4}$', v):
#             raise ValueError('Country code must be + followed by 1-4 digits')
#         return v
#
#     @field_validator('phone_number')
#     @classmethod
#     def validate_phone_number(cls, v: str) -> str:
#         # Remove common formatting characters
#         v = re.sub(r'[\s\-\(\)]', '', v)
#         if not re.match(r'^\d{6,15}$', v):
#             raise ValueError('Phone number must contain 6-15 digits')
#         return v
#
#
# class PhoneNumberCreate(PhoneNumberBase):
#     """Schema for creating phone number"""
#     user_id: PydanticObjectId = Field(..., description="Associated user ID")
#     is_primary: bool = Field(False, description="Is this the primary phone number")
#
#
# class PhoneNumberUpdate(BaseModel):
#     """Schema for updating phone number"""
#     country_code: Optional[str] = Field(None, max_length=4)
#     phone_number: Optional[str] = Field(None, max_length=20)
#     is_primary: Optional[bool] = None
#
#     @field_validator('country_code')
#     @classmethod
#     def validate_country_code(cls, v: Optional[str]) -> Optional[str]:
#         if v is not None:
#             v = v.strip()
#             if not v.startswith('+'):
#                 v = f'+{v}'
#             if not re.match(r'^\+\d{1,4}$', v):
#                 raise ValueError('Country code must be + followed by 1-4 digits')
#         return v
#
#     @field_validator('phone_number')
#     @classmethod
#     def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
#         if v is not None:
#             v = re.sub(r'[\s\-\(\)]', '', v)
#             if not re.match(r'^\d{6,15}$', v):
#                 raise ValueError('Phone number must contain 6-15 digits')
#         return v
#
#
# class PhoneNumberResponse(PhoneNumberBase):
#     """Schema for phone number response"""
#     id: PydanticObjectId = Field(..., alias="_id")
#     user_id: PydanticObjectId
#     is_verified: bool
#     is_primary: bool
#     verified_at: Optional[datetime] = None
#     created_at: datetime
#     updated_at: datetime
#
#     class Config:
#         populate_by_name = True
#         json_encoders = {
#             PydanticObjectId: str,
#             datetime: lambda v: v.isoformat()
#         }
#
#
# class PhoneVerificationRequest(BaseModel):
#     """Schema for phone verification request"""
#     code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
#
#     @field_validator('code')
#     @classmethod
#     def validate_code(cls, v: str) -> str:
#         if not v.isdigit():
#             raise ValueError('Verification code must be numeric')
#         return v
#
#
# # ============================================================
# # USER PREFERENCES SCHEMAS
# # ============================================================
#
# class UserPreferencesBase(BaseModel):
#     """Base schema for user preferences"""
#     email_notifications: bool = Field(True, description="Enable email notifications")
#     sms_notifications: bool = Field(False, description="Enable SMS notifications")
#     push_notifications: bool = Field(True, description="Enable push notifications")
#     language: str = Field("en", max_length=5, description="Preferred language code")
#     timezone: str = Field("UTC", description="User timezone")
#     theme: str = Field("light", pattern="^(light|dark|auto)$", description="UI theme preference")
#
#     @field_validator('timezone')
#     @classmethod
#     def validate_timezone(cls, v: str) -> str:
#         # Basic validation - you might want to use pytz for comprehensive validation
#         if not v or not isinstance(v, str):
#             return "UTC"
#         return v.strip()
#
#     @field_validator('language')
#     @classmethod
#     def validate_language(cls, v: str) -> str:
#         v = v.strip().lower()
#         # Basic validation for common language codes
#         if not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', v):
#             raise ValueError('Language must be a valid language code (e.g., en, en-US)')
#         return v
#
#
# class UserPreferencesCreate(UserPreferencesBase):
#     """Schema for creating user preferences"""
#     user_id: PydanticObjectId = Field(..., description="Associated user ID")
#
#
# class UserPreferencesUpdate(BaseModel):
#     """Schema for updating user preferences (all fields optional)"""
#     email_notifications: Optional[bool] = None
#     sms_notifications: Optional[bool] = None
#     push_notifications: Optional[bool] = None
#     language: Optional[str] = Field(None, max_length=5)
#     timezone: Optional[str] = None
#     theme: Optional[str] = Field(None, pattern="^(light|dark|auto)$")
#
#     @field_validator('timezone')
#     @classmethod
#     def validate_timezone(cls, v: Optional[str]) -> Optional[str]:
#         if v is not None:
#             return v.strip()
#         return v
#
#     @field_validator('language')
#     @classmethod
#     def validate_language(cls, v: Optional[str]) -> Optional[str]:
#         if v is not None:
#             v = v.strip().lower()
#             if not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', v):
#                 raise ValueError('Language must be a valid language code')
#         return v
#
#
# class UserPreferencesResponse(UserPreferencesBase):
#     """Schema for user preferences response"""
#     id: PydanticObjectId = Field(..., alias="_id")
#     user_id: PydanticObjectId
#     created_at: datetime
#     updated_at: datetime
#
#     class Config:
#         populate_by_name = True
#         json_encoders = {
#             PydanticObjectId: str,
#             datetime: lambda v: v.isoformat()
#         }
#
#
# # ============================================================
# # PAGINATION SCHEMAS
# # ============================================================
#
# class PaginatedResponse(BaseModel):
#     """Generic paginated response schema"""
#     items: list
#     total: int
#     page: int
#     per_page: int
#     total_pages: int
#     has_next: bool
#     has_prev: bool