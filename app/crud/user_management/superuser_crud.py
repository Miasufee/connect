import asyncio
import random
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.utils.generate import IDGenerator, IDPrefix
from app.core.utils.response.exceptions import Exceptions
from app.core.utils.response.success import Success
from app.core.utils.token_manager import token_manager
from app.models.user.user import User
from app.models.enums import UserRole
from app.crud.base import CrudBase
from app.core.security import security_manager
from app.schemas.user_schema import UserResponse


class SuperUserCrud(CrudBase[User]):
    def __init__(self):
        super().__init__(User)

    async def create_superuser(
            self,
            db: AsyncSession,
            email: str,
            password: str,
            secret_key: str
    ) -> User:
        """Create the one and only superuser with secret key check"""
        if secret_key != settings.API_SUPERUSER_SECRET_KEY:
            raise Exceptions.forbidden()

        existing = await self.get(db, role=UserRole.SUPERUSER)
        if existing:
            raise Exceptions.forbidden()

        hashed_pw = security_manager.hash_password(password)
        unique_id = IDGenerator.generate_id(IDPrefix.SUPERUSER, total_length=12)
        return await self.create(db, email=email, role=UserRole.SUPERUSER, hashed_password=hashed_pw, unique_id=unique_id)

    async def login_superuser(self, db: AsyncSession, email: str, password: str, unique_id: str):
        # Simulate delay to make timing attacks harder (between 50ms and 150ms)
        await asyncio.sleep(random.uniform(0.05, 0.15))

        # Try to get user
        db_user = await super().get(db=db,email=email)

        # If user not found, prepare a fake hash to simulate hashing cost
        fake_hash = security_manager.hash_password("fake_password")
        hashed_password_to_check = db_user.hashed_password if db_user else fake_hash

        # Always verify password, even if user doesn't exist
        password_ok = security_manager.verify_password(password, hashed_password_to_check)
        unique_id_ok = db_user.unique_id == unique_id

        # Combine all checks in one constant-time block
        checks_ok = (
                db_user is not None
                and password_ok
                and unique_id_ok
        )

        if not checks_ok:
            raise Exceptions.invalid_credentials()

        # Generate tokens
        tokens, expires = await token_manager.create_tokens(db, db_user)

        return Success.login_success(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            user=UserResponse.model_validate(db_user),
        )


super_user_crud = SuperUserCrud()
