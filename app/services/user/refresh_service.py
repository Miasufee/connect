from __future__ import annotations

from fastapi import Request
from typing import Tuple, Any
from app.core.utils.security import security_manager
from app.core.utils.token_manager import token_manager
from app.models.user_models import User


class RefreshService:
    """Handles refresh token validation, rotation, and user retrieval."""

    @staticmethod
    async def refresh_token_pair(request: Request) -> tuple[Any, Any, User]:
        """
        Validate the refresh token from the request, rotate it,
        and return the authenticated user along with a new access + refresh token pair.

        Args:
            request (Request): FastAPI request object.

        Returns:
            Tuple[str, str, User]: (access_token, refresh_token, user)
        """
        # Extract refresh token from headers or cookies
        user = await security_manager.get_user_from_refresh_token(request)
        access_token, refresh_token = await token_manager.generate_token_pair(user)

        return access_token, refresh_token, user
