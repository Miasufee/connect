import random
import asyncio
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import security_manager
from app.core.utils.response.exceptions import Exceptions
from app.core.utils.response.success import Success
from app.core.utils.token_manager import token_manager
from app.crud.user_management import user_crud
from app.models import UserRole
from app.schemas.user_schema import AdminUserCreate, UserResponse

router = APIRouter()

@router.post("/admin/login")
async def login_admin(payload: AdminUserCreate, db: AsyncSession = Depends(get_async_db)):
    # Simulate delay to make timing attacks harder (between 50ms and 150ms)
    await asyncio.sleep(random.uniform(0.05, 0.15))

    # Try to get user
    db_user = await user_crud.get_by_email(db, email=payload.email)

    # If user not found, prepare a fake hash to simulate hashing cost
    fake_hash = security_manager.hash_password("fake_password")
    hashed_password_to_check = db_user.hashed_password if db_user else fake_hash

    # Always verify password, even if user doesn't exist
    password_ok = security_manager.verify_password(payload.password, hashed_password_to_check)

    # Combine all checks in one constant-time block
    checks_ok = (
        db_user is not None
        and password_ok
        and db_user.is_email_verified
        and security_manager.constant_time_compare(db_user.role, UserRole.ADMIN)
        and db_user.admin_approval
        and security_manager.constant_time_compare(db_user.unique_id, payload.unique_id)
    )

    # Always return same response for any failure
    if not checks_ok:
        raise Exceptions.invalid_credentials()  # Generic error, no hints

    # Generate tokens
    tokens, expires = await token_manager.create_tokens(db, db_user)

    return Success.login_success(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        user=UserResponse.model_validate(db_user),
    )
