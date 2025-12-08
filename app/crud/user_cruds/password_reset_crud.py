from datetime import datetime, timezone
from typing import Optional
from app.crud.crud_base import CrudBase
from app.models.user_models import PasswordResetToken


class PasswordResetCRUD(CrudBase[PasswordResetToken]):
    """CRUD operations for password reset tokens."""

    def __init__(self):
        super().__init__(PasswordResetToken)

    async def create_token(self, email: str, token: str, expires_at: datetime) -> PasswordResetToken:
        """Create a new password reset token entry."""
        await self.revoke_all_user_tokens(email)
        # Ensure expires_at has timezone info
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        return await self.create(
            email=email,
            token=token,
            expires_at=expires_at,
            used=False
        )

    async def mark_token_used(self, token: str) -> Optional[PasswordResetToken]:
        """Mark a token as used and set used_at timestamp."""
        return await self.update_by_filter(
            filters={"token": token},
            update_data={
                "used": True,
                "used_at": datetime.now(timezone.utc)
            }
        )

    async def get_valid_token(self, token: str) -> Optional[PasswordResetToken]:
        """Retrieve a valid (unused and unexpired) token."""
        record = await self.get_one(token=token, used=False)

        if not record:
            return None

        # Ensure consistent timezone comparison
        if record.expires_at.tzinfo is None:
            record.expires_at = record.expires_at.replace(tzinfo=timezone.utc)

        # Check if token is expired using MongoDB-style comparison
        if datetime.now(timezone.utc) > record.expires_at:
            await self.delete(record.id)  # Clean up expired token
            return None

        return record

    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens and return count of deleted tokens."""
        current_time = datetime.now(timezone.utc)
        expired_tokens = await self.get_multi(
            filters={
                "expires_at": {"$lt": current_time}
            }
        )

        deleted_count = 0
        for token in expired_tokens:
            await self.delete(token.id)
            deleted_count += 1

        return deleted_count

    async def revoke_all_user_tokens(self, email: str) -> int:
        """Revoke all existing tokens for a user (when generating new one)."""
        active_tokens = await self.get_multi(
            filters={
                "email": email,
                "used": True
            }
        )

        revoked_count = 0
        for token in active_tokens:
            await self.mark_token_used(token.token)
            revoked_count += 1

        return revoked_count


# Global instance
password_reset_crud = PasswordResetCRUD()