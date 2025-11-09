import logging
from datetime import timezone


from starlette.responses import JSONResponse

from app.core.email_service import send_password_reset_email
from app.core.generator import GeneratorManager
from app.core.response.exceptions import Exceptions
from app.core.response.success import Success
from app.core.security import SecurityManager
from app.core.settings import settings
from app.crud import user_crud
from app.crud.password_reset_crud import password_reset_crud
from app.models.user_models import UserRole

logger = logging.getLogger(__name__)


class PasswordResetService:
    """Handles complete password reset flow - backend only."""

    @staticmethod
    async def request_password_reset(email: str, unique_id: str) -> JSONResponse:
        """
        Step 1: User requests password reset - send email with token.

        Args:
            email: User's email address

        Returns:
            Success response
            :param email:
            :param unique_id:
        """
        # Input validation
        if not email or unique_id:
            raise Exceptions.bad_request("Email is required")

        # Get user from database
        user = await user_crud.get_by_email(email)
        if not user:
            # Security: Don't reveal whether email exists
            logger.warning(f"Password reset attempted for non-existent email: {email}")
            return Success.ok(message="If the email exists, a reset link has been sent")

        # For admin/super users, require additional verification
        if user.user_role in [UserRole.admin, UserRole.super_admin, UserRole.superuser]:
            raise Exceptions.forbidden("Please use admin password reset flow")

        if user.unique_id != unique_id:
            logger.warning(f"Password reset attempted for non-existent unique_id: {unique_id}")
            return Success.ok(message="If the email unique, a reset link has been sent")

        try:
            # Revoke any existing tokens for this user
            await password_reset_crud.revoke_all_user_tokens(user.email)

            # Generate reset token
            reset_token = await SecurityManager.generate_password_reset_token(str(user.id))
            expires_at = GeneratorManager.expires_at(settings.PASSWORD_RESET_MINUTES_EXPIRE)

            # Ensure expires_at has timezone info
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            # Store token in database
            await password_reset_crud.create_token(
                email=user.email,
                token=reset_token,
                expires_at=expires_at
            )

            # Generate reset URL for email (frontend URL)
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}&email={user.email}"

            # Send email with reset link
            await send_password_reset_email(
                email=user.email,
                reset_url=reset_url,
                expires_in_minutes=settings.PASSWORD_RESET_MINUTES_EXPIRE
            )

            logger.info(f"Password reset email sent to: {email}")
            return Success.ok(message="If the email exists, a reset link has been sent")

        except Exception as e:
            logger.error(f"Error generating password reset token for {email}: {e}")
            raise Exceptions.internal_server_error("Could not process password reset request")

    @staticmethod
    async def validate_reset_token(email: str, token: str) -> dict:
        """
        Step 2: Validate reset token when frontend checks token validity.

        Args:
            email: User's email from URL
            token: Reset token from URL

        Returns:
            Validation result with user info if valid
        """
        if not email or not token:
            raise Exceptions.bad_request("Email and token are required")

        # Get and validate token
        db_token = await password_reset_crud.get_valid_token(token=token)
        if not db_token:
            raise Exceptions.forbidden("Invalid or expired reset token")

        # Verify token belongs to the correct email
        if db_token.email != email:
            raise Exceptions.forbidden("Token email mismatch")

        # Get user to return basic info (for frontend to display)
        user = await user_crud.get_by_email(email)
        if not user:
            raise Exceptions.forbidden("User not found")

        return {
            "valid": True,
            "email": user.email,
            "user_id": str(user.id),
            "expires_at": db_token.expires_at.isoformat(),
            "message": "Token is valid"
        }

    @staticmethod
    async def reset_password(
            email: str,
            token: str,
            new_password: str,
            confirm_password: str
    ) -> JSONResponse:
        """
        Step 3: Process password reset with new password from frontend.

        Args:
            email: User's email
            token: Reset token from email
            new_password: New password
            confirm_password: Password confirmation

        Returns:
            Success response
        """
        # Input validation
        if not all([email, token, new_password, confirm_password]):
            raise Exceptions.bad_request("All fields are required")

        if new_password != confirm_password:
            raise Exceptions.bad_request("Passwords do not match")


        # Get user
        user = await user_crud.get_by_email(email)
        if not user:
            raise Exceptions.forbidden("Invalid reset request")

        # Get and validate token
        db_token = await password_reset_crud.get_valid_token(token=token)
        if not db_token:
            raise Exceptions.forbidden("Invalid or expired reset token")

        if db_token.email != email:
            await password_reset_crud.mark_token_used(token)
            raise Exceptions.forbidden("Token email mismatch")

        # Verify JWT token signature
        try:
            verified_payload = await SecurityManager.verify_password_reset_token(token)
            token_user_id = verified_payload.get("sub")

            if token_user_id != str(user.id):
                await password_reset_crud.mark_token_used(token)
                raise Exceptions.forbidden("Token user mismatch")

        except Exception as e:
            await password_reset_crud.mark_token_used(token)
            logger.error(f"Token verification failed for {email}: {e}")
            raise Exceptions.forbidden("Invalid reset token")

        # Update password
        try:
            hashed_password = SecurityManager.hash_password(new_password)
            user.hashed_password = hashed_password
            user.token_version += 1  # Invalidate existing sessions
            await user.save()

            # Mark token as used
            await password_reset_crud.mark_token_used(token)

            # Clean up any expired tokens
            await password_reset_crud.cleanup_expired_tokens()

            logger.info(f"Password successfully reset for user: {email}")
            return Success.ok(message="Password reset successfully")

        except Exception as e:
            logger.error(f"Error updating password for {email}: {e}")
            raise Exceptions.internal_server_error("Could not reset password")


# Global instance
password_reset_service = PasswordResetService()