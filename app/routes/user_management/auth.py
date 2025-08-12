# from datetime import timedelta
# from typing import Any
# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.core.config import settings
# from app.core.database import get_async_db
# from app.core.security import security_manager
# from app.core.dependencies import get_current_user, get_current_active_user
# from app.crud.user_management import user_crud, refreshed_token_crud, verification_code_crud
# from app.schemas.user_schema import (
#     LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse,
#     ChangePasswordRequest, UserResponse, ResponseMessage
# )
# from app.schemas.auth_schemas import TokenPayload
# from app.services.user_service import user_service
#
# router = APIRouter()
#
#
# @router.post("/login", response_model=LoginResponse)
# async def login(
#     login_data: LoginRequest,
#     db: AsyncSession = Depends(get_async_db)
# ) -> Any:
#     """
#     OAuth2 compatible token login, get an access token for future requests
#     """
#     user = await security_manager.authenticate_user(
#         db, login_data.email, login_data.password
#     )
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#
#     # Create tokens
#     access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
#     refresh_token_expires = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
#
#     access_token = security_manager.create_access_token(
#         subject=user.id, expires_delta=access_token_expires
#     )
#     refresh_token = security_manager.create_refresh_token(
#         subject=user.id, expires_delta=refresh_token_expires
#     )
#
#     # Store refresh token in database
#     from datetime import datetime, timezone
#     expired_at = datetime.now(timezone.utc) + refresh_token_expires
#     await refreshed_token_crud.create_refresh_token(
#         db, user.id, refresh_token, expired_at
#     )
#
#     return LoginResponse(
#         access_token=access_token,
#         refresh_token=refresh_token,
#         token_type="bearer",
#         expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
#         user=UserResponse.model_validate(user)
#     )
#
#
# @router.post("/login/oauth2", response_model=LoginResponse)
# async def login_oauth2(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: AsyncSession = Depends(get_async_db)
# ) -> Any:
#     """
#     OAuth2 compatible token login using form data
#     """
#     user = await security_manager.authenticate_user(
#         db, form_data.username, form_data.password
#     )
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#
#     # Create tokens
#     access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
#     refresh_token_expires = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
#
#     access_token = security_manager.create_access_token(
#         subject=user.id, expires_delta=access_token_expires
#     )
#     refresh_token = security_manager.create_refresh_token(
#         subject=user.id, expires_delta=refresh_token_expires
#     )
#
#     # Store refresh token in database
#     from datetime import datetime, timezone
#     expired_at = datetime.now(timezone.utc) + refresh_token_expires
#     await refreshed_token_crud.create_refresh_token(
#         db, user.id, refresh_token, expired_at
#     )
#
#     return LoginResponse(
#         access_token=access_token,
#         refresh_token=refresh_token,
#         token_type="bearer",
#         expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
#         user=UserResponse.model_validate(user)
#     )
#
#
# @router.post("/refresh", response_model=RefreshTokenResponse)
# async def refresh_token(
#     refresh_data: RefreshTokenRequest,
#     db: AsyncSession = Depends(get_async_db)
# ) -> Any:
#     """
#     Refresh access token using refresh token
#     """
#     # Verify refresh token
#     user_id = security_manager.verify_token(
#         refresh_data.refresh_token, token_type="refresh"
#     )
#     if not user_id:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid refresh token"
#         )
#
#     # Check if refresh token exists in database
#     stored_token = await refreshed_token_crud.get_valid_token(
#         db, refresh_data.refresh_token
#     )
#     if not stored_token:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Refresh token not found or expired"
#         )
#
#     # Create new access token
#     access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = security_manager.create_access_token(
#         subject=user_id, expires_delta=access_token_expires
#     )
#
#     return RefreshTokenResponse(
#         access_token=access_token,
#         token_type="bearer",
#         expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
#     )
#
#
# @router.post("/logout", response_model=ResponseMessage)
# async def logout(
#     refresh_data: RefreshTokenRequest,
#     current_user: UserResponse = Depends(get_current_user),
#     db: AsyncSession = Depends(get_async_db)
# ) -> Any:
#     """
#     Logout user by revoking refresh token
#     """
#     # Revoke the specific refresh token
#     await refreshed_token_crud.revoke_token(db, refresh_data.refresh_token)
#
#     return ResponseMessage(message="Successfully logged out")
#
#
# @router.post("/logout-all", response_model=ResponseMessage)
# async def logout_all(
#     current_user: UserResponse = Depends(get_current_user),
#     db: AsyncSession = Depends(get_async_db)
# ) -> Any:
#     """
#     Logout user from all devices by revoking all refresh tokens
#     """
#     await refreshed_token_crud.revoke_all_user_tokens(db, current_user.id)
#
#     return ResponseMessage(message="Successfully logged out from all devices")
#
#
# @router.post("/change-password", response_model=ResponseMessage)
# async def change_password(
#     password_data: ChangePasswordRequest,
#     current_user: UserResponse = Depends(get_current_active_user),
#     db: AsyncSession = Depends(get_async_db)
# ) -> Any:
#     """
#     Change user password
#     """
#     # Validate password match
#     try:
#         password_data.validate_passwords_match()
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )
#
#     # Change password using service
#     try:
#         await user_service.change_password(
#             db,
#             current_user.id,
#             password_data.current_password,
#             password_data.new_password
#         )
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )
#
#     return ResponseMessage(message="Password changed successfully")
#
#
# @router.get("/me", response_model=UserResponse)
# async def read_users_me(
#     current_user: UserResponse = Depends(get_current_user)
# ) -> Any:
#     """
#     Get current user
#     """
#     return current_user
#
#
# @router.post("/verify-token", response_model=UserResponse)
# async def verify_token(
#     current_user: UserResponse = Depends(get_current_user)
# ) -> Any:
#     """
#     Verify if token is valid and return user info
#     """
#     return current_user
