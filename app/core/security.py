import logging
import secrets
import time
import hmac
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
    """ security manager with centralized token utilities."""

    # --------------------------------------------------------------------------
    # BASIC UTILITIES
    # --------------------------------------------------------------------------

    @staticmethod
    def now() -> int:
        return int(time.time())

    @staticmethod
    def hash_password(password: str) -> str:
        if not password:
            raise ValueError("Password required")
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return bool(plain and hashed and pwd_context.verify(plain, hashed))

    @staticmethod
    def constant_time_compare(a: float, b: float) -> bool:
        return hmac.compare_digest(str(a).encode(), str(b).encode())

    @staticmethod
    def random_jti() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_secure_random_string(length: int = 32) -> str:
        return secrets.token_urlsafe(length)

    # --------------------------------------------------------------------------
    # TOKEN HANDLING (CENTRALIZED)
    # --------------------------------------------------------------------------

    @staticmethod
    def _decode(token: str, secret: str, algo: str) -> Dict[str, Any]:
        try:
            return jwt.decode(token, secret, algorithms=[algo])
        except ExpiredSignatureError:
            logger.warning("Token expired")
            raise Exceptions.token_expired_exception()
        except JWTError as e:
            logger.error(f"Invalid token: {e}")
            raise Exceptions.permission_denied()

    @staticmethod
    def _validate_claims(payload: Dict[str, Any], expected_type: str):
        if payload.get("type") != expected_type:
            raise Exceptions.permission_denied()
        if not payload.get("sub"):
            raise Exceptions.permission_denied()

    # --------------------------------------------------------------------------
    # TOKEN GENERATION HELPERS
    # --------------------------------------------------------------------------

    @staticmethod
    def _create_token(user_id: str, token_type: str, expires_in: int,
                      version: int = 1, secret=None, algo=None) -> str:

        secret = secret or settings.JWT_SECRET_KEY
        algo = algo or settings.JWT_ALGORITHM

        now = SecurityManager.now()
        payload = {
            "sub": str(user_id),
            "exp": now + expires_in,
            "iat": now,
            "jti": SecurityManager.random_jti(),
            "version": version,
            "type": token_type
        }
        return jwt.encode(payload, secret, algorithm=algo)

    # --------------------------------------------------------------------------
    # ACCESS / REFRESH TOKENS
    # --------------------------------------------------------------------------

    @staticmethod
    async def generate_access_token(user_id: str, version: int = 1) -> str:
        return SecurityManager._create_token(
            user_id=user_id,
            token_type="access",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            version=version,
        )

    @staticmethod
    async def generate_refresh_token(user_id: str, version: int = 1) -> str:
        return SecurityManager._create_token(
            user_id=user_id,
            token_type="refresh",
            expires_in=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            version=version,
        )

    @staticmethod
    def verify_access_token(token: str) -> Dict[str, Any]:
        payload = SecurityManager._decode(
            token,
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM
        )
        SecurityManager._validate_claims(payload, "access")
        return payload

    @staticmethod
    def verify_refresh_token(token: str) -> Dict[str, Any]:
        payload = SecurityManager._decode(
            token,
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM
        )
        SecurityManager._validate_claims(payload, "refresh")
        return payload

    # --------------------------------------------------------------------------
    # PASSWORD RESET TOKENS
    # --------------------------------------------------------------------------

    @staticmethod
    def generate_password_reset_token(user_id: str) -> str:
        return SecurityManager._create_token(
            user_id=user_id,
            token_type="password_reset",
            expires_in=settings.PASSWORD_RESET_MINUTES_EXPIRE * 60,
            secret=settings.PASSWORD_RESET_SECRET_KEY,
            algo=settings.PASSWORD_RESET_ALGORITHM,
        )

    @staticmethod
    def verify_password_reset_token(token: str) -> Dict[str, Any]:
        payload = SecurityManager._decode(
            token,
            settings.PASSWORD_RESET_SECRET_KEY,
            settings.PASSWORD_RESET_ALGORITHM
        )
        SecurityManager._validate_claims(payload, "password_reset")
        return payload

    # --------------------------------------------------------------------------
    # EMAIL VERIFICATION
    # --------------------------------------------------------------------------

    @staticmethod
    def generate_email_verification_token(user_id: str) -> str:
        return SecurityManager._create_token(
            user_id=user_id,
            token_type="email_verification",
            expires_in=24 * 3600,
        )

    @staticmethod
    def verify_email_verification_token(token: str) -> Dict[str, Any]:
        payload = SecurityManager._decode(
            token,
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM
        )
        SecurityManager._validate_claims(payload, "email_verification")
        return payload

    # --------------------------------------------------------------------------
    # CURRENT USER EXTRACTION
    # --------------------------------------------------------------------------

    @staticmethod
    async def get_token(request: Request) -> str:
        return (
                request.cookies.get("access_token")
                or request.headers.get("Authorization", "").replace("Bearer ", "")
                or request.headers.get("X-Access-Token")
                or Exceptions.permission_denied()
        )

    @staticmethod
    async def get_current_user(request: Request) -> User:
        token = await SecurityManager.get_token(request)
        payload = SecurityManager.verify_access_token(token)

        user_id = payload["sub"]
        user = await user_crud.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise Exceptions.permission_denied()

        if user.token_version != payload.get("version"):
            raise Exceptions.permission_denied()

        return user

    # --------------------------------------------------------------------------
    # SESSION INVALIDATION
    # --------------------------------------------------------------------------

    @staticmethod
    async def invalidate_user_sessions(user_id: str) -> None:
        try:
            user = await User.get(user_id)
            if user:
                user.token_version += 1
                await user.save()
                logger.info(f"Sessions invalidated for user {user_id}")
        except Exception as e:
            logger.error(f"Session invalidation failed: {e}")
            raise


security_manager = SecurityManager()

