"""
User service layer that combines CRUD operations with business logic and schema validation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.crud.user_management import (
    user_crud, user_profile_crud, phone_number_crud, 
    address_crud, social_account_crud
)
from app.schemas.user_schema import (
    UserCreate, UserCreateInternal, UserUpdate, UserResponse,
  UserProfileCreate,
    PhoneNumberCreate, SocialAccountCreate,
    PaginatedResponse
)
from app.models.enums import UserRole, SocialProvider

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    async def create_user(
        self,
        db: AsyncSession,
        user_create: UserCreate
    ) -> UserResponse:
        """Create a new user with validation"""
        # Validate password match
        user_create.validate_passwords_match()
        
        # Check if user already exists
        existing_user = await user_crud.get_by_email(db, user_create.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash password and create internal schema
        hashed_password = self.hash_password(user_create.password)
        user_internal = UserCreateInternal(
            email=user_create.email,
            hashed_password=hashed_password,
            role=user_create.role,
            is_email_verified=user_create.is_email_verified,
            admin_approval=user_create.admin_approval,
            unique_id=user_create.unique_id
        )
        
        return await user_crud.create_user_with_schema(db, user_internal)
    
    async def get_user_by_id(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Optional[UserResponse]:
        """Get user by ID"""
        user = await user_crud.get(db, obj_id=user_id)
        return UserResponse.model_validate(user) if user else None
    
    async def get_user_with_profile(
        self,
        db: AsyncSession,
        user_id: int
    ):
        """Get user with profile"""
        user = await user_crud.get_user_with_profile(db, user_id)
        return UserResponse.model_validate(user) if user else None
    
    async def update_user(
        self,
        db: AsyncSession,
        user_id: int,
        user_update: UserUpdate
    ) -> UserResponse:
        """Update user"""
        # Check if user exists
        existing_user = await user_crud.get(db, obj_id=user_id)
        if not existing_user:
            raise ValueError("User not found")
        
        # Check email uniqueness if email is being updated
        if user_update.email and user_update.email != existing_user.email:
            email_exists = await user_crud.get_by_email(db, user_update.email)
            if email_exists:
                raise ValueError("Email already in use")
        
        return await user_crud.update_user_with_schema(db, user_id, user_update)
    
    async def get_users_paginated(
        self,
        db: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        role: Optional[UserRole] = None,
        is_verified: Optional[bool] = None
    ) -> PaginatedResponse[UserResponse]:
        """Get paginated users"""
        filters = {}
        if role:
            filters['role'] = role
        if is_verified is not None:
            filters['is_email_verified'] = is_verified
            
        return await user_crud.get_users_paginated(
            db, page=page, per_page=per_page, **filters
        )
    
    async def create_complete_user(
        self,
        db: AsyncSession,
        user_create: UserCreate,
        profile_data: Optional[dict] = None,
        phone_data: Optional[dict] = None,
        address_data: Optional[dict] = None
    ):
        """Create user with all related data"""
        # Create user
        user_response = await self.create_user(db, user_create)
        user_id = user_response.id
        
        # Create profile if data provided
        profile = None
        if profile_data:
            profile_create = UserProfileCreate(user_id=user_id, **profile_data)
            profile = await user_profile_crud.create_profile_with_schema(db, profile_create)
        
        # Create phone if data provided
        phones = []
        if phone_data:
            phone_create = PhoneNumberCreate(user_id=user_id, **phone_data)
            phone = await phone_number_crud.create_phone_with_schema(db, phone_create)
            phones = [phone]
        
        # Create address if data provided
        addresses = []
        if address_data:
            address_create = AddressCreate(user_id=user_id, **address_data)
            address = await address_crud.create_address_with_schema(db, address_create)
            addresses = [address]
        
        # Return complete user data
        return UserResponse(
            **user_response.model_dump(),
            profile=profile,
            phone_numbers=phones,
            addresses=addresses,
            social_accounts=[]
        )
    
    async def authenticate_user(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ) -> Optional[UserResponse]:
        """Authenticate user with email and password"""
        user = await user_crud.get_by_email(db, email)
        if not user or not user.hashed_password:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        return UserResponse.model_validate(user)
    
    async def change_password(
        self,
        db: AsyncSession,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> UserResponse:
        """Change user password"""
        user = await user_crud.get(db, obj_id=user_id)
        if not user:
            raise ValueError("User not found")
        
        if not user.hashed_password or not self.verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")
        
        hashed_new_password = self.hash_password(new_password)
        return await user_crud.update_password(db, user_id, hashed_new_password)


user_service = UserService()
