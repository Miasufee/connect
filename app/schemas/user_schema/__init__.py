from .user_schemas import *
from .auth_schemas import *
from .common_schemas import *
from .phone_number_schemas import *
from .refresh_token_schemas import *
from .social_account_schemas import *
from .user_profile_schemas import *
from .verification_code_schemas import *
from .refresh_token_schemas import *


# from .user_schemas import (
#     UserBase, UserCreate, UserCreateInternal, UserUpdate,
#     UserPasswordUpdate, UserResponse, UserLogin, UserEmailVerification, UserEmail, SuperUserCreate, SuperUserLogin
# )
# from .user_profile_schemas import (
#     UserProfileBase, UserProfileCreate, UserProfileUpdate, UserProfileResponse
# )
# from .phone_number_schemas import (
#     PhoneNumberBase, PhoneNumberCreate, PhoneNumberUpdate, PhoneNumberResponse
# )
# from .address_schemas import (
#     AddressBase, AddressCreate, AddressUpdate, AddressResponse
# )
# from .social_account_schemas import (
#     SocialAccountBase, SocialAccountCreate, SocialAccountUpdate, SocialAccountResponse
# )
# from .verification_code_schemas import (
#     VerificationCodeBase, VerificationCodeCreate, VerificationCodeVerify, VerificationCodeResponse
# )
# from .refresh_token_schemas import (
#     RefreshTokenBase, RefreshTokenCreate, RefreshTokenResponse, RefreshTokenVerify
# )
# from .common_schemas import (
#     PaginatedResponse, SearchParams, FilterParams, ResponseMessage, ErrorResponse
# )
#
# # Forward references for relationships
# UserProfileResponse.model_rebuild()
# # UserWithProfile.model_rebuild()
# # UserWithRelations.model_rebuild()
#
# __all__ = [
#     # User schemas
#     "UserBase", "UserCreate", "UserCreateInternal", "UserUpdate",
#     "UserPasswordUpdate", "UserResponse", "UserLogin", "UserEmailVerification", "UserEmail",
#
#     # User profile schemas
#     "UserProfileBase", "UserProfileCreate", "UserProfileUpdate", "UserProfileResponse",
#
#     # Phone number schemas
#     "PhoneNumberBase", "PhoneNumberCreate", "PhoneNumberUpdate", "PhoneNumberResponse",
#
#     # Address schemas
#     "AddressBase", "AddressCreate", "AddressUpdate", "AddressResponse",
#
#     # Social account schemas
#     "SocialAccountBase", "SocialAccountCreate", "SocialAccountUpdate", "SocialAccountResponse",
#
#     # Verification code schemas
#     "VerificationCodeBase", "VerificationCodeCreate", "VerificationCodeVerify", "VerificationCodeResponse",
#
#     # Refresh token schemas
#     "RefreshTokenBase", "RefreshTokenCreate", "RefreshTokenResponse", "RefreshTokenVerify",
#
#     # Common schemas
#     "PaginatedResponse", "SearchParams", "FilterParams", "ResponseMessage", "ErrorResponse"
# ]
