from datetime import datetime, timedelta, timezone
from jose import JWTError
from typing import Tuple, Optional

from app.models.user_models import User, RefreshedToken
from app.crud.contents_cruds.refreshed_token_crud import refreshed_token_crud
from app.core.settings import settings
from app.core.security import SecurityManager


class Token:
    """Represents access and refresh token pair."""
    def __init__(self, access_token: str, refresh_token: str, token_type: str = "bearer"):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type


class TokenManager:
    """Handles creation, validation, rotation, revocation, and cleanup of tokens."""

    # -----------------------
    # Token Generation
    # -----------------------
    @staticmethod
    async def create_access_token(user_id: str, token_version: int = 1) -> str:
        return await SecurityManager.generate_access_token(user_id, token_version)

    @staticmethod
    async def create_refresh_token(user_id: str, token_version: int = 1) -> str:
        exp = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        token = await SecurityManager.generate_refresh_token(user_id, token_version)
        await refreshed_token_crud.create_refresh_token(
            user_id=user_id,
            refresh_token=token,
            expires_at=exp
        )
        return token

    # -----------------------
    # Token Rotation & Validation
    # -----------------------
    @staticmethod
    async def _verify_refresh_token(refresh_token: str) -> Optional[RefreshedToken]:
        try:
            payload = SecurityManager.verify_refresh_token(refresh_token)
            user_id = payload.get("sub")
            if not user_id:
                return None

            token_record = await refreshed_token_crud.get_valid_token(refresh_token=refresh_token)
            if not token_record or token_record.expires_at < datetime.now(timezone.utc):
                await refreshed_token_crud.revoke_token(refresh_token)
                return None

            return token_record
        except (JWTError, ValueError):
            return None

    @staticmethod
    async def rotate_refresh_token(old_token: str) -> Optional[Token]:
        token_record = await TokenManager._verify_refresh_token(old_token)
        if not token_record:
            return None

        user = await token_record.user.fetch()
        if not user:
            await refreshed_token_crud.revoke_token(old_token)
            return None

        # Revoke old token and issue new pair
        await refreshed_token_crud.revoke_token(old_token)
        access_token = await TokenManager.create_access_token(str(user.id), user.token_version)
        refresh_token = await TokenManager.create_refresh_token(str(user.id), user.token_version)

        return Token(access_token=access_token, refresh_token=refresh_token)

    # -----------------------
    # Logout / Revocation
    # -----------------------
    @staticmethod
    async def logout_current_device(refresh_token: str) -> bool:
        """Revoke the provided refresh token (logout current device)."""
        return await TokenManager.revoke_token(refresh_token)

    @staticmethod
    async def logout_all_other_devices(user: User, current_refresh_token: str) -> int:
        """Revoke all refresh tokens for a user except the current one."""
        all_tokens = await refreshed_token_crud.get_user_tokens(user_id=str(user.id))
        revoked_count = 0
        for token in all_tokens:
            if token.refresh_token != current_refresh_token:
                await refreshed_token_crud.revoke_token(token.refresh_token)
                revoked_count += 1
        return revoked_count

    @staticmethod
    async def logout_all_devices(user_id: str) -> int:
        """Revoke all refresh tokens for a user (all devices)."""
        return await refreshed_token_crud.revoke_user_tokens(user_id=user_id)

    # -----------------------
    # Cleanup
    # -----------------------
    @staticmethod
    async def revoke_expired_tokens() -> int:
        return await refreshed_token_crud.revoke_expired_tokens()

    @staticmethod
    async def cleanup_tokens() -> Tuple[int, int]:
        revoked_deleted = await refreshed_token_crud.purge_revoked_tokens(older_than_days=30)
        expired_deleted = await refreshed_token_crud.cleanup_expired_tokens(older_than_days=7)
        return revoked_deleted, expired_deleted

    # -----------------------
    # Token Pair Helper
    # -----------------------
    @staticmethod
    async def generate_token_pair(user: User) -> Tuple[str, str]:
        access_token = await TokenManager.create_access_token(str(user.id), user.token_version)
        refresh_token = await TokenManager.create_refresh_token(str(user.id), user.token_version)
        return access_token, refresh_token

    # -----------------------
    # Single Token Revoke
    # -----------------------
    @staticmethod
    async def revoke_token(refresh_token: str) -> bool:
        token = await refreshed_token_crud.revoke_token(refresh_token)
        return bool(token)

    @staticmethod
    async def revoke_user_tokens(user_id: str) -> int:
        return await refreshed_token_crud.revoke_user_tokens(user_id=user_id)



token_manager = TokenManager()
