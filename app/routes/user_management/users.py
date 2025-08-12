# from typing import Any, List
# from fastapi import APIRouter, Depends, HTTPException, status, Query
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.core.database import get_async_db
# from app.core.dependencies import (
#     get_current_user, get_current_active_user,
#     get_current_admin_user, get_current_superuser
# )
# from app.crud.user_management import user_crud, user_profile_crud
# from app.schemas.user_schema import (
#     UserCreate, UserUpdate, UserResponse,
#     PaginatedResponse, ResponseMessage,
#     UserProfileCreate, UserProfileUpdate, UserProfileResponse
# )
# from app.services.user_service import user_service
# from app.models.enums import UserRole
#
# router = APIRouter()
#
#
# @router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# async def create_user(
#     user_create: UserCreate,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_admin_user)
# ) -> Any:
#     """
#     Create new user (Admin only)
#     """
#     try:
#         user = await user_service.create_user(db, user_create)
#         return user
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )
#
#
# @router.get("/", response_model=PaginatedResponse[UserResponse])
# async def read_users(
#     page: int = Query(1, ge=1),
#     per_page: int = Query(20, ge=1, le=100),
#     role: UserRole = Query(None),
#     is_verified: bool = Query(None),
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_admin_user)
# ) -> Any:
#     """
#     Retrieve users with pagination (Admin only)
#     """
#     return await user_service.get_users_paginated(
#         db, page=page, per_page=per_page, role=role, is_verified=is_verified
#     )
#
#
# @router.get("/search", response_model=List[UserResponse])
# async def search_users(
#     q: str = Query(..., min_length=1, max_length=100),
#     skip: int = Query(0, ge=0),
#     limit: int = Query(20, ge=1, le=100),
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_admin_user)
# ) -> Any:
#     """
#     Search users by email or unique_id (Admin only)
#     """
#     users = await user_crud.search_users(db, q, skip=skip, limit=limit)
#     return [UserResponse.model_validate(user) for user in users]
#
#
# @router.get("/me", response_model=dict)
# async def read_user_me(
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_user)
# ) -> Any:
#     """
#     Get current user with profile
#     """
#     user_with_profile = await user_service.get_user_with_profile(db, current_user.id)
#     if not user_with_profile:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
#     return user_with_profile
#
#
# @router.put("/me", response_model=UserResponse)
# async def update_user_me(
#     user_update: UserUpdate,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_active_user)
# ) -> Any:
#     """
#     Update current user
#     """
#     try:
#         return await user_service.update_user(db, current_user.id, user_update)
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )
#
#
# @router.get("/{user_id}", response_model=dict)
# async def read_user(
#     user_id: int,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_admin_user)
# ) -> Any:
#     """
#     Get user by ID with profile (Admin only)
#     """
#     user = await user_service.get_user_with_profile(db, user_id)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
#     return user
#
#
# @router.put("/{user_id}", response_model=UserResponse)
# async def update_user(
#     user_id: int,
#     user_update: UserUpdate,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_admin_user)
# ) -> Any:
#     """
#     Update user by ID (Admin only)
#     """
#     try:
#         return await user_service.update_user(db, user_id, user_update)
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )
#
#
# @router.delete("/{user_id}", response_model=ResponseMessage)
# async def delete_user(
#     user_id: int,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_superuser)
# ) -> Any:
#     """
#     Delete user by ID (Superuser only)
#     """
#     user = await user_crud.get(db, obj_id=user_id)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
#
#     await user_crud.delete(db, obj_id=user_id)
#     return ResponseMessage(message="User deleted successfully")
#
#
# @router.post("/{user_id}/verify-email", response_model=ResponseMessage)
# async def verify_user_email(
#     user_id: int,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_admin_user)
# ) -> Any:
#     """
#     Verify user email (Admin only)
#     """
#     user = await user_crud.get(db, obj_id=user_id)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
#
#     await user_crud.verify_email(db, user_id)
#     return ResponseMessage(message="User email verified successfully")
#
#
# @router.post("/{user_id}/approve", response_model=ResponseMessage)
# async def approve_user(
#     user_id: int,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_admin_user)
# ) -> Any:
#     """
#     Approve user (Admin only)
#     """
#     user = await user_crud.get(db, obj_id=user_id)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
#
#     await user_crud.approve_user(db, user_id)
#     return ResponseMessage(message="User approved successfully")
#
#
# # User Profile endpoints
# @router.post("/me/profile", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
# async def create_user_profile(
#     profile_create: UserProfileCreate,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_active_user)
# ) -> Any:
#     """
#     Create profile for current user
#     """
#     # Ensure user is creating their own profile
#     if profile_create.user_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Can only create your own profile"
#         )
#
#     # Check if profile already exists
#     existing_profile = await user_profile_crud.get_by_user_id(db, current_user.id)
#     if existing_profile:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Profile already exists"
#         )
#
#     return await user_profile_crud.create_profile_with_schema(db, profile_create)
#
#
# @router.put("/me/profile", response_model=UserProfileResponse)
# async def update_user_profile(
#     profile_update: UserProfileUpdate,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_active_user)
# ) -> Any:
#     """
#     Update profile for current user
#     """
#     try:
#         return await user_profile_crud.update_profile_with_schema(
#             db, current_user.id, profile_update
#         )
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=str(e)
#         )
