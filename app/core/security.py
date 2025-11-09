import logging
import secrets
import time
import hmac
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import Request
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext

from app.core.response.exceptions import Exceptions
from app.core.settings import settings
from app.crud import user_crud
from app.models.user_models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


class SecurityManager:
    """Enhanced security manager with comprehensive token handling and security best practices."""


    @staticmethod
    def hash_password(password: str) -> str:
        """Hash the password using bcrypt."""
        if not password:
            raise ValueError("Password cannot be empty")
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify plain password against hashed password."""
        if not plain_password or not hashed_password:
            return False
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def verify_access_token(token: str) -> Dict[str, Any]:
        """
        Verify access token validity and return payload.

        Args:
            token: JWT access token

        Returns:
            Dict with token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            # Additional payload validation
            if not payload.get("sub"):
                raise Exceptions.permission_denied()

            if payload.get("type") and payload["type"] != "access":
                raise Exceptions.permission_denied()

            return payload

        except ExpiredSignatureError:
            logger.warning("Access token expired")
            raise Exceptions.token_expired_exception()
        except JWTError as e:
            logger.error(f"Invalid access token: {e}")
            raise Exceptions.permission_denied()

    @staticmethod
    def verify_refresh_token(token: str) -> Dict[str, Any]:
        """
        Verify refresh token validity and return payload.

        Args:
            token: JWT refresh token

        Returns:
            Dict with token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            # Validate refresh token specific claims
            if not payload.get("sub"):
                raise Exceptions.permission_denied()

            if payload.get("type") and payload["type"] != "refresh":
                raise Exceptions.permission_denied()

            return payload

        except ExpiredSignatureError:
            logger.warning("Refresh token expired")
            raise Exceptions.refresh_token_expired_exception()
        except JWTError as e:
            logger.error(f"Invalid refresh token: {e}")
            raise Exceptions.permission_denied()

    @staticmethod
    def constant_time_compare(val1: float, val2: float) -> bool:
        """
        Constant time comparison to prevent timing attacks.

        Args:
            val1: First value to compare
            val2: Second value to compare

        Returns:
            bool: True if values are equal
        """
        return hmac.compare_digest(str(val1).encode(), str(val2).encode())

    @staticmethod
    def _generate_jti() -> str:
        """Generate a unique JWT ID using cryptographically secure random."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def _get_current_timestamp() -> int:
        """Get current timestamp in seconds."""
        return int(time.time())

    @staticmethod
    async def get_token(request: Request) -> str:
        """
        Extract access token from cookies or Authorization header.

        Args:
            request: FastAPI request object

        Returns:
            str: JWT token string

        Raises:
            HTTPException: If no token found
        """
        # Check cookies first
        token = request.cookies.get("access_token")
        if token:
            return token

        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.replace("Bearer ", "")

        # Check X-Access-Token header as fallback
        token = request.headers.get("X-Access-Token")
        if token:
            return token

        logger.warning("No access token found in request")
        raise Exceptions.permission_denied()

    @staticmethod
    async def get_current_user(request: Request) -> User:
        """
        Get current user from token with comprehensive validation.

        Args:
            request: FastAPI request object

        Returns:
            User: Authenticated user object

        Raises:
            HTTPException: If user not found or token invalid
        """
        token = await SecurityManager.get_token(request)
        payload = SecurityManager.verify_access_token(token)

        user_id = payload.get("sub")
        if not user_id:
            logger.error("Token missing subject claim")
            raise Exceptions.permission_denied()

        try:
            user = await user_crud.get_by_ids(user_id)
            if not user:
                logger.warning(f"User not found for ID: {user_id}")
                raise Exceptions.permission_denied()

            if not user.is_active:
                logger.warning(f"Inactive user attempted access: {user_id}")
                raise Exceptions.forbidden("Account deactivated")

            # Validate token version for forced logout
            token_version = payload.get("version", 0)
            if user.token_version != token_version:
                logger.warning(f"Token version mismatch for user: {user_id}")
                raise Exceptions.permission_denied()

            return user

        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            raise Exceptions.permission_denied()

    @staticmethod
    async def generate_access_token(user_id: str, token_version: int = 1) -> str:
        """
        Generate short-lived access token.

        Args:
            user_id: User identifier
            token_version: Token version for invalidation

        Returns:
            str: JWT access token
        """
        payload = {
            "sub": str(user_id),
            "exp": SecurityManager._get_current_timestamp() + (settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60),
            "iat": SecurityManager._get_current_timestamp(),
            "jti": SecurityManager._generate_jti(),
            "version": token_version,
            "type": "access"
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    async def generate_refresh_token(user_id: str, token_version: int = 1) -> str:
        """
        Generate long-lived refresh token.

        Args:
            user_id: User identifier
            token_version: Token version for invalidation

        Returns:
            str: JWT refresh token
        """
        payload = {
            "sub": str(user_id),
            "exp": SecurityManager._get_current_timestamp() + (settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60),
            "iat": SecurityManager._get_current_timestamp(),
            "jti": SecurityManager._generate_jti(),
            "version": token_version,
            "type": "refresh"
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    async def generate_password_reset_token(user_id: str) -> str:
        """
        Generate password reset token with dedicated secret and algorithm.

        Args:
            user_id: User identifier

        Returns:
            str: JWT password reset token
        """
        payload = {
            "sub": str(user_id),
            "exp": SecurityManager._get_current_timestamp() + (settings.PASSWORD_RESET_MINUTES_EXPIRE * 60),
            "iat": SecurityManager._get_current_timestamp(),
            "jti": SecurityManager._generate_jti(),
            "type": "password_reset"
        }
        return jwt.encode(
            payload,
            settings.PASSWORD_RESET_SECRET_KEY,
            algorithm=settings.PASSWORD_RESET_ALGORITHM
        )

    @staticmethod
    async def verify_password_reset_token(token: str) -> Dict[str, Any]:
        """
        Verify password reset token validity and return payload.

        Args:
            token: Password reset JWT token

        Returns:
            Dict with token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.PASSWORD_RESET_SECRET_KEY,
                algorithms=[settings.PASSWORD_RESET_ALGORITHM]
            )

            # Validate reset token specific claims
            if not payload.get("sub"):
                raise Exceptions.permission_denied()

            if payload.get("type") != "password_reset":
                raise Exceptions.permission_denied()

            return payload

        except ExpiredSignatureError:
            logger.warning("Password reset token expired")
            raise Exceptions.token_expired_exception("Reset token has expired")
        except JWTError as e:
            logger.error(f"Invalid password reset token: {e}")
            raise Exceptions.permission_denied()

    @staticmethod
    def is_token_expired(expires_at: datetime) -> bool:
        """
        Check if token is expired with proper timezone handling.

        Args:
            expires_at: Expiration datetime

        Returns:
            bool: True if token is expired
        """
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > expires_at

    @staticmethod
    async def generate_email_verification_token(user_id: str) -> str:
        """
        Generate email verification token.

        Args:
            user_id: User identifier

        Returns:
            str: JWT email verification token
        """
        payload = {
            "sub": str(user_id),
            "exp": SecurityManager._get_current_timestamp() + (24 * 60 * 60),  # 24 hours
            "iat": SecurityManager._get_current_timestamp(),
            "jti": SecurityManager._generate_jti(),
            "type": "email_verification"
        }
        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,  # Use main JWT secret for email verification
            algorithm=settings.JWT_ALGORITHM
        )

    @staticmethod
    async def verify_email_verification_token(token: str) -> Dict[str, Any]:
        """
        Verify email verification token.

        Args:
            token: Email verification JWT token

        Returns:
            Dict with token payload
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            if payload.get("type") != "email_verification":
                raise Exceptions.permission_denied()

            return payload

        except ExpiredSignatureError:
            logger.warning("Email verification token expired")
            raise Exceptions.token_expired_exception("Verification token expired")
        except JWTError as e:
            logger.error(f"Invalid email verification token: {e}")
            raise Exceptions.permission_denied()

    @staticmethod
    async def invalidate_user_sessions(user_id: str) -> None:
        """
        Invalidate all user sessions by incrementing token version.

        Args:
            user_id: User identifier
        """
        try:
            user = await User.get(user_id)
            if user:
                user.token_version += 1
                await user.save()
                logger.info(f"Invalidated all sessions for user: {user_id}")
        except Exception as e:
            logger.error(f"Error invalidating sessions for user {user_id}: {e}")
            raise

    @staticmethod
    def generate_secure_random_string(length: int = 32) -> str:
        """
        Generate cryptographically secure random string.

        Args:
            length: Length of the random string

        Returns:
            str: Random string
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def validate_csrf_token(provided_token: str, expected_token: str) -> bool:
        """
        Validate CSRF token using constant-time comparison.

        Args:
            provided_token: Token from client request
            expected_token: Token from session

        Returns:
            bool: True if tokens match
        """
        return SecurityManager.constant_time_compare(provided_token, expected_token)


# Global instance
security_manager = SecurityManager()

# import logging
# import secrets
# import string
# import time
# import hmac
# from fastapi import Request
# from jose import jwt, JWTError, ExpiredSignatureError
# from passlib.context import CryptContext
# from app.core.response.exceptions import Exceptions
# from app.core.settings import settings
# from app.models.user_models import User
#
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# logger = logging.getLogger(__name__)
#
#
# class SecurityManager:
#     """Handles authentication, password hashing, and role-based authorization."""
#
#     @staticmethod
#     def hash_password(password: str) -> str:
#         """Hash the password"""
#         return pwd_context.hash(password)
#
#     @staticmethod
#     def verify_password(plain_password: str, hashed_password: str) -> bool:
#         """Verify plain and hashed password"""
#         return pwd_context.verify(plain_password, hashed_password)
#
#     @staticmethod
#     def verify_access_token(token: str) -> dict:
#         """Verify access token validity and return payload"""
#         try:
#             payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
#             return payload
#         except ExpiredSignatureError:
#             logger.warning("Access token expired.")
#             raise Exceptions.token_expired_exception()
#         except JWTError as e:
#             logger.error(f"Invalid access token: {e}")
#             raise Exceptions.credentials_exception()
#
#     @staticmethod
#     def verify_refresh_token(token: str) -> dict:
#         """Verify refresh token validity and return payload"""
#         try:
#             payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
#             return payload
#         except ExpiredSignatureError:
#             logger.warning("Refresh token expired.")
#             raise Exceptions.refresh_token_expired_exception()
#         except JWTError as e:
#             logger.error(f"Invalid refresh token: {e}")
#             raise Exceptions.credentials_exception()
#
#     @staticmethod
#     def constant_time_compare(val1: str, val2: str):
#         """Constant time compare"""
#         return hmac.compare_digest(str(val1), str(val2))
#
#     @staticmethod
#     def _generate_jti() -> str:
#         """Generate a unique JWT ID"""
#         return "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
#
#     @staticmethod
#     async def get_token(request: Request) -> str:
#         """Get access token from cookies or headers"""
#         token = request.cookies.get("access_token")
#         if not token:
#             auth_header = request.headers.get("Authorization")
#             if auth_header and auth_header.startswith("Bearer "):
#                 token = auth_header.replace("Bearer ", "")
#         if not token:
#             raise Exceptions.credentials_exception()
#         return token
#
#     @staticmethod
#     async def get_current_user(request: Request) -> User:
#         """Get current user from token"""
#         token = await SecurityManager.get_token(request)
#         payload = SecurityManager.verify_access_token(token)
#         user_id = payload.get("sub")
#
#         if not user_id:
#             raise Exceptions.credentials_exception()
#
#         user = await User.get(user_id)
#         if not user:
#             raise Exceptions.credentials_exception()
#
#         token_version = payload.get("version", 0)
#         if user.token_version != token_version:
#             raise Exceptions.credentials_exception()
#
#         return user
#
#     @staticmethod
#     async def generate_access_token(user_id: str, token_version: int = 1) -> str:
#         """Generate short-lived access token"""
#         payload = {
#             "sub": str(user_id),
#             "exp": int(time.time()) + (settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60),
#             "jti": SecurityManager._generate_jti(),
#             "version": token_version
#         }
#         return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
#
#     @staticmethod
#     async def generate_refresh_token(user_id: str, token_version: int = 1) -> str:
#         """Generate long-lived refresh token"""
#         payload = {
#             "sub": str(user_id),
#             "exp": int(time.time()) + (settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60),
#             "jti": SecurityManager._generate_jti(),
#             "version": token_version
#         }
#         return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
#
#     @staticmethod
#     async def generate_password_reset_token(user_id: str):
#         payload = {
#             "sub": str(user_id),
#             "exp": int(time.time()) + settings.PASSWORD_RESET_MINUTES_EXPIRE,
#             "jti": SecurityManager._generate_jti()
#         }
#         return jwt.encode(payload, settings.PASSWORD_RESET_SECRET_KEY, algorithm=settings.PASSWORD_RESET_ALGORITHM)
#
#     @staticmethod
#     async def verify_reset_token(token: str) -> dict:
#         """Verify reset token validity and return payload"""
#         return jwt.decode(token, settings.PASSWORD_RESET_SECRET_KEY, algorithms=[settings.PASSWORD_RESET_ALGORITHM])
#
#
# security_manager = SecurityManager()
