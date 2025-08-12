# from typing import Any, List
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.core.database import get_async_db
# from app.core.dependencies import get_current_active_user
# from app.crud.user_management import address_crud
# from app.schemas.user_schema import UserResponse, ResponseMessage
# from app.schemas.user_schema.address_schemas import (
#     AddressCreate, AddressUpdate, AddressResponse,
#
# )
#
# router = APIRouter()
#
#
# @router.get("/", response_model=List[AddressResponse])
# async def get_user_addresses(
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_active_user)
# ) -> Any:
#     """
#     Get current user's addresses
#     """
#     return await address_crud.get_user_addresses_with_schema(db, current_user.id)
#
#
# @router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
# async def create_address(
#     address_create: AddressCreate,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_active_user)
# ) -> Any:
#     """
#     Create address for current user
#     """
#     # Ensure user is creating their own address
#     if address_create.user_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Can only create your own address"
#         )
#
#     return await address_crud.create_address_with_schema(db, address_create)
#
#
# @router.put("/{address_id}", response_model=AddressResponse)
# async def update_address(
#     address_id: int,
#     address_update: AddressUpdate,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_active_user)
# ) -> Any:
#     """
#     Update address
#     """
#     # Check if address exists and belongs to current user
#     address = await address_crud.get(db, obj_id=address_id)
#     if not address:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Address not found"
#         )
#
#     if address.user_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Can only update your own address"
#         )
#
#     return await address_crud.update_address_with_schema(db, address_id, address_update)
#
#
# @router.delete("/{address_id}", response_model=ResponseMessage)
# async def delete_address(
#     address_id: int,
#     db: AsyncSession = Depends(get_async_db),
#     current_user: UserResponse = Depends(get_current_active_user)
# ) -> Any:
#     """
#     Delete address
#     """
#     # Check if address exists and belongs to current user
#     address = await address_crud.get(db, obj_id=address_id)
#     if not address:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Address not found"
#         )
#
#     if address.user_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Can only delete your own address"
#         )
#
#     await address_crud.delete(db, obj_id=address_id)
#     return ResponseMessage(message="Address deleted successfully")
