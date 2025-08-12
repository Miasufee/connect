# from typing import Any, List
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.core.database import get_async_db
# from app.core.dependencies import get_current_active_user
# from app.crud.user_management import phone_number_crud
# from app.schemas.user_schema import (
#     PhoneNumberCreate, PhoneNumberUpdate, PhoneNumberResponse,
#     ResponseMessage, UserResponse
# )
#
# router = APIRouter()
#
#
# @router.get("/", response_model=List[PhoneNumberResponse])
# async def get_user_phone_numbers(
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_active_user)
# ) -> Any:
#     """
#     Get current user's phone numbers
#     """
#     return await phone_number_crud.get_user_phones_with_schema(db, current_user.id)
#
#
# @router.post("/", response_model=PhoneNumberResponse, status_code=status.HTTP_201_CREATED)
# async def create_phone_number(
#     phone_create: PhoneNumberCreate,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_active_user)
# ) -> Any:
#     """
#     Create phone number for current user
#     """
#     # Ensure user is creating their own phone number
#     if phone_create.user_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Can only create your own phone number"
#         )
#
#     # Check if phone number already exists
#     exists = await phone_number_crud.phone_exists(
#         db, phone_create.country_code, phone_create.phone_number
#     )
#     if exists:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Phone number already exists"
#         )
#
#     return await phone_number_crud.create_phone_with_schema(db, phone_create)
#
#
# @router.put("/{phone_id}", response_model=PhoneNumberResponse)
# async def update_phone_number(
#     phone_id: int,
#     phone_update: PhoneNumberUpdate,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_active_user)
# ) -> Any:
#     """
#     Update phone number
#     """
#     # Check if phone number exists and belongs to current user
#     phone = await phone_number_crud.get(db, obj_id=phone_id)
#     if not phone:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Phone number not found"
#         )
#
#     if phone.user_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Can only update your own phone number"
#         )
#
#     return await phone_number_crud.update_phone_with_schema(db, phone_id, phone_update)
#
#
# @router.delete("/{phone_id}", response_model=ResponseMessage)
# async def delete_phone_number(
#     phone_id: int,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_active_user)
# ) -> Any:
#     """
#     Delete phone number
#     """
#     # Check if phone number exists and belongs to current user
#     phone = await phone_number_crud.get(db, obj_id=phone_id)
#     if not phone:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Phone number not found"
#         )
#
#     if phone.user_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Can only delete your own phone number"
#         )
#
#     await phone_number_crud.delete(db, obj_id=phone_id)
#     return ResponseMessage(message="Phone number deleted successfully")
#
#
# @router.post("/{phone_id}/verify", response_model=ResponseMessage)
# async def verify_phone_number(
#     phone_id: int,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_active_user)
# ) -> Any:
#     """
#     Verify phone number (placeholder - would integrate with SMS service)
#     """
#     # Check if phone number exists and belongs to current user
#     phone = await phone_number_crud.get(db, obj_id=phone_id)
#     if not phone:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Phone number not found"
#         )
#
#     if phone.user_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Can only verify your own phone number"
#         )
#
#     await phone_number_crud.verify_phone_number(db, phone_id)
#     return ResponseMessage(message="Phone number verified successfully")
