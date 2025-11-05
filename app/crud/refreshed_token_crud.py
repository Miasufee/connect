from datetime import datetime, timezone, timedelta
from typing import Optional, Sequence
import logging

from beanie import SortDirection
from app.crud.crud_base import CrudBase
from app.models.user_models import RefreshedToken

logger = logging.getLogger(__name__)


class RefreshedTokenCrud(CrudBase[RefreshedToken]):
    """CRUD operations for managing refresh tokens using Beanie + CrudBase with revocation."""

    def __init__(self):
        super().__init__(RefreshedToken)

    # ------------------------
    # Create
    # ------------------------
    async def create_refresh_token(
            self,
            user_id: str,
            refresh_token: str,
            expires_at: datetime
    ) -> Optional[RefreshedToken]:
        """Create and save a new refresh token with error handling."""
        try:
            return await self.create(
                user_id=user_id,
                refresh_token=refresh_token,
                expires_at=expires_at,
                created_at=datetime.now(timezone.utc),
                revoked=False,
            )
        except Exception as e:
            logger.error(f"Failed to create refresh token for user {user_id}: {str(e)}")
            return None

    # ------------------------
    # Read
    # ------------------------
    async def get_valid_token(
            self,
            refresh_token: str
    ) -> Optional[RefreshedToken]:
        """Retrieve a valid, non-expired, non-revoked refresh token."""
        try:
            now = datetime.now(timezone.utc)
            return await self.get_one(
                refresh_token=refresh_token,
                expires_at={"$gt": now},
                revoked=False,
            )
        except Exception as e:
            logger.error(f"Error retrieving valid token: {str(e)}")
            return None

    async def get_user_tokens(
            self,
            user_id: str
    ) -> Sequence[RefreshedToken]:
        """Get all tokens for a user (newest first)."""
        try:
            return await self.get_multi(
                user_id=user_id,
                order_by=[("created_at", SortDirection.DESCENDING)]
            )
        except Exception as e:
            logger.error(f"Error retrieving tokens for user {user_id}: {str(e)}")
            return []

    # ------------------------
    # Update (Revocation) - Production Optimized
    # ------------------------
    async def revoke_token(self, refresh_token: str) -> Optional[RefreshedToken]:
        """Mark a specific token as revoked instead of deleting."""
        try:
            token = await self.get_one(refresh_token=refresh_token)
            if token:
                token.revoked = True
                token.revoked_at = datetime.now(timezone.utc)
                await token.save()
                logger.info(f"Token revoked: {refresh_token}")
            return token
        except Exception as e:
            logger.error(f"Error revoking token {refresh_token}: {str(e)}")
            return None

    async def revoke_user_tokens(self, user_id: str) -> int:
        """
        Mark all active tokens of a user as revoked.
        Uses MongoDB bulk update for optimal performance.
        """
        try:
            result = await self.model.find(
                {"user_id": user_id, "revoked": False}
            ).update_many(
                {"$set": {
                    "revoked": True,
                    "revoked_at": datetime.now(timezone.utc)
                }}
            )
            modified_count = result.modified_count if result else 0
            logger.info(f"Revoked {modified_count} tokens for user {user_id}")
            return modified_count
        except Exception as e:
            logger.error(f"Error revoking tokens for user {user_id}: {str(e)}")
            return 0

    async def revoke_expired_tokens(self) -> int:
        """
        Mark all expired tokens as revoked.
        Uses MongoDB bulk update for optimal performance.
        """
        try:
            now = datetime.now(timezone.utc)
            result = await self.model.find(
                {"expires_at": {"$lte": now}, "revoked": False}
            ).update_many(
                {"$set": {"revoked": True, "revoked_at": now}}
            )
            modified_count = result.modified_count if result else 0
            if modified_count > 0:
                logger.info(f"Automatically revoked {modified_count} expired tokens")
            return modified_count
        except Exception as e:
            logger.error(f"Error revoking expired tokens: {str(e)}")
            return 0

    # ------------------------
    # Cleanup & Maintenance
    # ------------------------
    async def purge_revoked_tokens(self, older_than_days: int = 30) -> int:
        """
        Physically delete old revoked tokens to free up storage.
        Only removes tokens revoked more than specified days ago.
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)
            result = await self.model.find({
                "revoked": True,
                "revoked_at": {"$lte": cutoff_date}
            }).delete_many()

            deleted_count = result.deleted_count if result else 0
            if deleted_count > 0:
                logger.info(f"Purged {deleted_count} revoked tokens older than {older_than_days} days")
            return deleted_count
        except Exception as e:
            logger.error(f"Error purging revoked tokens: {str(e)}")
            return 0

    async def cleanup_expired_tokens(self, older_than_days: int = 7) -> int:
        """
        Comprehensive cleanup: remove expired tokens (both revoked and non-revoked)
        that expired more than specified days ago.
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)
            result = await self.model.find({
                "expires_at": {"$lte": cutoff_date}
            }).delete_many()

            deleted_count = result.deleted_count if result else 0
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired tokens older than {older_than_days} days")
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {str(e)}")
            return 0

    # ------------------------
    # Analytics & Monitoring
    # ------------------------
    async def get_token_stats(self) -> dict:
        """Get statistics about tokens for monitoring purposes."""
        try:
            now = datetime.now(timezone.utc)

            # Use aggregation for efficient counting
            pipeline = [
                {
                    "$facet": {
                        "total_tokens": [{"$count": "count"}],
                        "active_tokens": [
                            {"$match": {"revoked": False, "expires_at": {"$gt": now}}},
                            {"$count": "count"}
                        ],
                        "revoked_tokens": [
                            {"$match": {"revoked": True}},
                            {"$count": "count"}
                        ],
                        "expired_tokens": [
                            {"$match": {"expires_at": {"$lte": now}}},
                            {"$count": "count"}
                        ]
                    }
                }
            ]

            results = await self.model.aggregate(pipeline).to_list()
            stats = results[0] if results else {}

            return {
                "total": stats.get("total_tokens", [{}])[0].get("count", 0),
                "active": stats.get("active_tokens", [{}])[0].get("count", 0),
                "revoked": stats.get("revoked_tokens", [{}])[0].get("count", 0),
                "expired": stats.get("expired_tokens", [{}])[0].get("count", 0),
                "timestamp": now.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting token stats: {str(e)}")
            return {
                "total": 0,
                "active": 0,
                "revoked": 0,
                "expired": 0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }


# Instance
refreshed_token_crud = RefreshedTokenCrud()