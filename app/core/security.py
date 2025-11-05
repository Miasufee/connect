import logging
import secrets
import string
import time
import hmac
from fastapi import Request
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from app.core.response.exceptions import Exceptions
from app.core.settings import settings
from app.models.user_models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


class SecurityManager:
    """Handles authentication, password hashing, and role-based authorization."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash the password"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify plain and hashed password"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def verify_access_token(token: str) -> dict:
        """Verify access token validity and return payload"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except ExpiredSignatureError:
            logger.warning("Access token expired.")
            raise Exceptions.token_expired_exception()
        except JWTError as e:
            logger.error(f"Invalid access token: {e}")
            raise Exceptions.credentials_exception()

    @staticmethod
    def verify_refresh_token(token: str) -> dict:
        """Verify refresh token validity and return payload"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except ExpiredSignatureError:
            logger.warning("Refresh token expired.")
            raise Exceptions.refresh_token_expired_exception()
        except JWTError as e:
            logger.error(f"Invalid refresh token: {e}")
            raise Exceptions.credentials_exception()

    @staticmethod
    def constant_time_compare(val1: str, val2: str):
        """Constant time compare"""
        return hmac.compare_digest(str(val1), str(val2))

    @staticmethod
    def _generate_jti() -> str:
        """Generate a unique JWT ID"""
        return "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

    @staticmethod
    async def get_token(request: Request) -> str:
        """Get access token from cookies or headers"""
        token = request.cookies.get("access_token")
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
        if not token:
            raise Exceptions.credentials_exception()
        return token

    @staticmethod
    async def get_current_user(request: Request) -> User:
        """Get current user from token"""
        token = await SecurityManager.get_token(request)
        payload = SecurityManager.verify_access_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise Exceptions.credentials_exception()

        user = await User.get(user_id)
        if not user:
            raise Exceptions.credentials_exception()

        token_version = payload.get("version", 0)
        if user.token_version != token_version:
            raise Exceptions.credentials_exception()

        return user

    @staticmethod
    def generate_access_token(user_id: str, token_version: int = 1) -> str:
        """Generate short-lived access token"""
        payload = {
            "sub": str(user_id),
            "exp": int(time.time()) + (settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60),
            "jti": SecurityManager._generate_jti(),
            "version": token_version
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def generate_refresh_token(user_id: str, token_version: int = 1) -> str:
        """Generate long-lived refresh token"""
        payload = {
            "sub": str(user_id),
            "exp": int(time.time()) + (settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60),
            "jti": SecurityManager._generate_jti(),
            "version": token_version
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


security_manager = SecurityManager()
