from pydantic import EmailStr
from starlette.responses import JSONResponse

from app.core.security import SecurityManager
from app.core.token_manager import token_manager
from app.core.response.exceptions import Exceptions
from app.core.response.success import Success
from app.crud import user_crud
from app.models.user_models import UserRole


class AdminAuthService:
    """Handles login for superuser, super_admin, and admin users."""

    @staticmethod
    async def login(email: EmailStr, unique_id: str, password: str) -> JSONResponse:
        """
        Login flow for superuser, super_admin, or admin.

        Args:
            email (EmailStr): User email.
            unique_id (str): Unique ID assigned to user.
            password (str): Plain password.

        Returns:
            Success: Access and refresh tokens with user info.
        """
        user = await user_crud.get_by_email(email)
        if not user.is_email_verified:
            raise Exceptions.not_verified(detail="Email not verified")

        if (
            not user
            or user.user_role not in [UserRole.superuser, UserRole.super_admin, UserRole.admin]
            or not SecurityManager.verify_password(password, user.hashed_password)
            or user.unique_id != unique_id
        ):
            SecurityManager.constant_time_compare("0.5", "i.5")
            raise Exceptions.forbidden(detail="Invalid credentials")

        access_token, refresh_token = await token_manager.generate_token_pair(user)
        await user_crud.update_last_login(str(user.id))
        return Success.login_success(access_token, refresh_token, user)


admin_auth_service = AdminAuthService()