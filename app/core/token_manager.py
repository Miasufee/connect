from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional

from app.core.response.exceptions import Exceptions
from app.models.user_models import User, RefreshedToken
from app.crud.user_cruds.refreshed_token_crud import refreshed_token_crud
from app.core.settings import settings
from app.core.security import SecurityManager


class Token:
    """Represents an access and refresh token pair."""
    def __init__(self, access_token: str, refresh_token: str, token_type: str = "bearer"):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type


class TokenManager:
    """Centralized token management: creation, validation, rotation, revocation, cleanup."""

    # -----------------------
    # Internal Helpers
    # -----------------------
    @staticmethod
    async def _create_token(user_id: str, token_type: str, version: int = 1) -> str:
        """Generic token creation wrapper."""
        if token_type == "access":
            return SecurityManager.generate_access_token(user_id, version)
        elif token_type == "refresh":
            token = SecurityManager.generate_refresh_token(user_id, version)
            exp = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
            await refreshed_token_crud.create_refresh_token(
                user_id=user_id, refresh_token=token, expires_at=exp
            )
            return token
        raise ValueError(f"Unsupported token type: {token_type}")

    @staticmethod
    async def _revoke_tokens(tokens: list[RefreshedToken], exclude: Optional[str] = None) -> int:
        """Revoke multiple tokens, optionally excluding one."""
        count = 0
        for token in tokens:
            if token.refresh_token != exclude:
                await refreshed_token_crud.revoke_token(token.refresh_token)
                count += 1
        return count

    @staticmethod
    async def _verify_refresh_token(refresh_token: str) -> Optional[RefreshedToken]:
        """Validate refresh token and return token record if valid."""
        try:
            _ = SecurityManager.verify_refresh_token(refresh_token)
            token_record = await refreshed_token_crud.get_valid_token(refresh_token)
            if not token_record or token_record.expires_at < datetime.now(timezone.utc):
                await refreshed_token_crud.revoke_token(refresh_token)
                return None
            return token_record
        except Exceptions.forbidden():
            return None

    # -----------------------
    # Public Token Generation
    # -----------------------
    @staticmethod
    async def create_access_token(user_id: str, token_version: int = 1) -> str:
        return await TokenManager._create_token(user_id, "access", token_version)

    @staticmethod
    async def create_refresh_token(user_id: str, token_version: int = 1) -> str:
        return await TokenManager._create_token(user_id, "refresh", token_version)

    @staticmethod
    async def generate_token_pair(user: User) -> Tuple[str, str]:
        """Generate access + refresh token pair."""
        access = await TokenManager.create_access_token(str(user.id), user.token_version)
        refresh = await TokenManager.create_refresh_token(str(user.id), user.token_version)
        return access, refresh

    # -----------------------
    # Token Rotation
    # -----------------------
    @staticmethod
    async def rotate_refresh_token(old_token: str) -> Optional[Token]:
        token_record = await TokenManager._verify_refresh_token(old_token)
        if not token_record:
            return None

        user = await token_record.user.fetch()
        if not user:
            await refreshed_token_crud.revoke_token(old_token)
            return None

        await refreshed_token_crud.revoke_token(old_token)
        access = await TokenManager.create_access_token(str(user.id), user.token_version)
        refresh = await TokenManager.create_refresh_token(str(user.id), user.token_version)
        return Token(access, refresh)

    # -----------------------
    # Logout / Revocation
    # -----------------------
    @staticmethod
    async def logout_current_device(refresh_token: str) -> bool:
        return bool(await refreshed_token_crud.revoke_token(refresh_token))

    @staticmethod
    async def logout_all_other_devices(user: User, current_refresh_token: str) -> int:
        tokens = await refreshed_token_crud.get_user_tokens(str(user.id))
        return await TokenManager._revoke_tokens(tokens, exclude=current_refresh_token)

    @staticmethod
    async def logout_all_devices(user_id: str) -> int:
        return await refreshed_token_crud.revoke_user_tokens(user_id=user_id)

    # -----------------------
    # Cleanup
    # -----------------------
    @staticmethod
    async def cleanup_tokens() -> Tuple[int, int]:
        revoked = await refreshed_token_crud.purge_revoked_tokens(older_than_days=30)
        expired = await refreshed_token_crud.cleanup_expired_tokens(older_than_days=7)
        return revoked, expired

token_manager = TokenManager()