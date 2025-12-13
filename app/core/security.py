from __future__ import annotations

import logging
import secrets
import time
import hmac
from dataclasses import dataclass
from typing import Dict, Any, ClassVar
from fastapi import Request
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext

from app.core.response.exceptions import Exceptions
from app.core.settings import settings
from app.crud import user_crud
from app.models.user_models import User

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass(frozen=True)
class TokenConfig:
    """
    Configuration for a specific token type.

    Attributes:
        secret (str): Secret key used to sign the token.
        algorithm (str): JWT algorithm to use (e.g., "HS256").
        expire_seconds (int): Token expiration time in seconds.
        allow_login (bool): Whether this token type is allowed for login.
    """
    secret: str
    algorithm: str
    expire_seconds: int
    allow_login: bool = False


class SecurityManager:
    """
    Centralized manager for authentication and token handling.

    Handles:
        - Password hashing & verification
        - JWT token creation, verification, and claim validation
        - Session invalidation
        - Secure random token generation
    """

    _configs: ClassVar[Dict[str, TokenConfig]]

    @classmethod
    def initialize(cls) -> None:
        """Load token configurations from settings."""
        cls._configs = settings.DEFAULT_TOKEN_CONFIGS

    @staticmethod
    def now() -> int:
        """Return current UNIX timestamp as integer."""
        return int(time.time())

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plaintext password using bcrypt.

        Args:
            password (str): The password to hash (minimum 8 characters).

        Raises:
            ValueError: If password is too short or empty.

        Returns:
            str: Hashed password string.
        """
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """
        Verify a plaintext password against a hashed password.

        Args:
            plain (str): Plaintext password.
            hashed (str): Hashed password.

        Returns:
            bool: True if verified, False otherwise.
        """
        return bool(plain and hashed and pwd_context.verify(plain, hashed))

    @staticmethod
    def constant_time_compare(a: bytes | str, b: bytes | str) -> bool:
        """
        Compare two strings or bytes in constant time to prevent timing attacks.

        Args:
            a, b (str | bytes): Values to compare.

        Returns:
            bool: True if equal, False otherwise.
        """
        a_bytes = a.encode() if isinstance(a, str) else a
        b_bytes = b.encode() if isinstance(b, str) else b
        return hmac.compare_digest(a_bytes, b_bytes)

    @staticmethod
    def random_jti() -> str:
        """Generate a secure random JWT ID (jti)."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_secure_random_string(length: int = 32) -> str:
        """
        Generate a cryptographically secure random string.

        Args:
            length (int): Minimum length (16+ recommended).

        Raises:
            ValueError: If length < 16.

        Returns:
            str: Secure random string.
        """
        if length < 16:
            raise ValueError("Length must be at least 16 for security")
        return secrets.token_urlsafe(length)

    @classmethod
    def _get_config(cls, token_type: str) -> TokenConfig:
        """
        Retrieve the configuration for a specific token type.

        Args:
            token_type (str): Token type (access, refresh, etc.).

        Raises:
            Exceptions.internal_server_error: If token type is invalid.

        Returns:
            TokenConfig: Configuration for the token type.
        """
        cfg = cls._configs.get(token_type)
        if not cfg:
            logger.error("Unknown token type: %s", token_type)
            raise Exceptions.internal_server_error(f"Invalid token type: {token_type}")
        return cfg

    @staticmethod
    def _encode(payload: Dict[str, Any], secret: str, algorithm: str) -> str:
        """Encode a payload into a JWT string."""
        return jwt.encode(payload, secret, algorithm=algorithm)

    @staticmethod
    def _decode(token: str, secret: str, algorithm: str) -> Dict[str, Any]:
        """
        Decode a JWT token.

        Args:
            token (str): JWT string.
            secret (str): Secret key used to sign token.
            algorithm (str): Algorithm used for signing.

        Raises:
            Exceptions.token_expired_exception: If token is expired.
            Exceptions.permission_denied: If token is invalid.

        Returns:
            dict: Decoded JWT payload.
        """
        try:
            return jwt.decode(token, secret, algorithms=[algorithm])
        except ExpiredSignatureError:
            logger.warning("Token expired")
            raise Exceptions.token_expired_exception()
        except JWTError as e:
            logger.warning("Invalid token: %s", e)
            raise Exceptions.permission_denied()

    @classmethod
    def _validate_claims(cls, payload: Dict[str, Any], expected_type: str) -> None:
        """
        Validate token claims: type, subject, and login permissions.

        Args:
            payload (dict): Decoded token payload.
            expected_type (str): Expected token type.

        Raises:
            Exceptions.permission_denied: If claims are invalid or login not allowed.
        """
        if payload.get("type") != expected_type:
            logger.warning("Token type mismatch: expected %s, got %s", expected_type, payload.get("type"))
            raise Exceptions.permission_denied()

        if not payload.get("sub"):
            logger.warning("Token missing subject claim")
            raise Exceptions.permission_denied()

        cfg = cls._get_config(expected_type)
        if not cfg.allow_login and payload.get("type") in ["access", "refresh"]:
            logger.warning("Token type %s not allowed for login", payload.get("type"))
            raise Exceptions.permission_denied()

    @classmethod
    def create_token(cls, user_id: str, token_type: str, version: int = 1) -> str:
        """
        Create a JWT token for a given user and token type.

        Args:
            user_id (str): ID of the user.
            token_type (str): Type of token ("access", "refresh", etc.).
            version (int): Token version for session invalidation.

        Returns:
            str: Signed JWT token.
        """
        cfg = cls._get_config(token_type)
        now = cls.now()

        payload = {
            "sub": str(user_id),
            "exp": now + cfg.expire_seconds,
            "iat": now,
            "jti": cls.random_jti(),
            "version": version,
            "type": token_type,
        }
        return cls._encode(payload, cfg.secret, cfg.algorithm)

    @classmethod
    def generate_access_token(cls, user_id: str, version: int = 1) -> str:
        """Generate a standard access token."""
        return cls.create_token(user_id, "access", version)

    @classmethod
    def generate_refresh_token(cls, user_id: str, version: int = 1) -> str:
        """Generate a refresh token."""
        return cls.create_token(user_id, "refresh", version)

    @classmethod
    def generate_password_reset_token(cls, user_id: str) -> str:
        """Generate a token for password reset flow."""
        return cls.create_token(user_id, "password_reset")

    @classmethod
    def generate_email_verification_token(cls, user_id: str) -> str:
        """Generate a token for email verification flow."""
        return cls.create_token(user_id, "email_verification")

    @classmethod
    def verify_token(cls, token: str, token_type: str) -> Dict[str, Any]:
        """
        Verify a token for a given type and validate its claims.

        Args:
            token (str): JWT token string.
            token_type (str): Expected token type.

        Returns:
            dict: Validated token payload.
        """
        cfg = cls._get_config(token_type)
        payload = cls._decode(token, cfg.secret, cfg.algorithm)
        cls._validate_claims(payload, token_type)
        return payload

    @classmethod
    def verify_access_token(cls, token: str) -> Dict[str, Any]:
        """Verify an access token."""
        return cls.verify_token(token, "access")

    @classmethod
    def verify_refresh_token(cls, token: str) -> Dict[str, Any]:
        """Verify a refresh token."""
        return cls.verify_token(token, "refresh")

    @classmethod
    def verify_password_reset_token(cls, token: str) -> Dict[str, Any]:
        """Verify a password reset token."""
        return cls.verify_token(token, "password_reset")

    @classmethod
    def verify_email_verification_token(cls, token: str) -> Dict[str, Any]:
        """Verify an email verification token."""
        return cls.verify_token(token, "email_verification")

    @staticmethod
    async def extract_access_token(request: Request) -> str:
        """
        Extract access token from request headers or cookies.

        Args:
            request (Request): FastAPI request object.

        Raises:
            Exceptions.permission_denied: If no token is found.

        Returns:
            str: JWT token string.
        """
        token = (
            request.cookies.get("access_token")
            or request.headers.get("Authorization", "").replace("Bearer ", "")
            or request.headers.get("X-Access-Token")
        )

        if not token:
            logger.warning("No token found in request")
            raise Exceptions.permission_denied()

        return token

    @staticmethod
    async def extract_refresh_token(request: Request) -> str:
        """
        Extract refresh token from request headers or cookies.

        Args:
            request (Request): FastAPI request object.

        Raises:
            Exceptions.permission_denied: If no token is found.

        Returns:
            str: JWT refresh token string.
        """
        refresh_token = (
                request.cookies.get("refresh_token")
                or request.headers.get("Authorization", "").replace("Bearer ", "")
                or request.headers.get("X-Refresh-Token")
        )

        if not refresh_token:
            raise Exceptions.permission_denied("Refresh token not provided")

        return refresh_token
    @classmethod
    async def get_current_user(cls, request: Request) -> User:
        """
        Get the currently authenticated user based on access token.

        Args:
            request (Request): FastAPI request object.

        Raises:
            Exceptions.permission_denied: If user is not found, inactive, or token version mismatch.

        Returns:
            User: Authenticated user object.
        """
        token = await cls.extract_access_token(request)
        payload = cls.verify_access_token(token)

        user = await user_crud.get_user_by_id(payload["sub"])
        if not user or not getattr(user, "is_active", True):
            logger.warning("User not found or inactive: %s", payload["sub"])
            raise Exceptions.permission_denied()

        if payload.get("version", 0) != getattr(user, "token_version", 0):
            logger.info("Token version mismatch for user %s", user.id)
            raise Exceptions.permission_denied()

        return user

    @classmethod
    async def get_user_from_refresh_token(cls, request: Request) -> User:
        """
        Extract the refresh token from request, verify it, and return the user.

        Args:
            request (Request): FastAPI request object.

        Raises:
            Exceptions.permission_denied: If token invalid, user inactive, or version mismatch.

        Returns:
            User: Authenticated user object.
        """
        # Extract refresh token from cookies or headers
        refresh_token = await cls.extract_refresh_token(request)

        # Verify refresh token and get payload
        payload = cls.verify_refresh_token(refresh_token)

        # Fetch user from database
        user = await user_crud.get_user_by_id(payload["sub"])
        if not user or not getattr(user, "is_active", True):
            raise Exceptions.permission_denied("User not found or inactive")

        # Check token version
        if payload.get("version", 0) != getattr(user, "token_version", 0):
            raise Exceptions.permission_denied("Token version mismatch")

        return user

    @staticmethod
    async def invalidate_user_sessions(user_id: str) -> None:
        """
        Invalidate all active sessions for a user by incrementing token version.

        Args:
            user_id (str): ID of the user.

        Raises:
            Exception: If session invalidation fails.
        """
        try:
            user = await User.get(user_id)
            if user:
                user.token_version = getattr(user, "token_version", 0) + 1
                await user.save()
                logger.info("Invalidated sessions for user %s", user_id)
        except Exception as e:
            logger.error("Session invalidation failed for %s: %s", user_id, e)
            raise


# Initialize token configurations
SecurityManager.initialize()
security_manager = SecurityManager
