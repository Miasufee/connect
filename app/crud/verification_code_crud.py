from datetime import datetime, timezone
from .crud_base import CrudBase
from app.models.user_models import VerificationCode
from app.core.response.exceptions import Exceptions
from app.core.generator import GeneratorManager


class VerificationCodeCrud(CrudBase[VerificationCode]):
    def __init__(self):
        super().__init__(VerificationCode)

    async def create_verification_code(self, user_id: str):
        """Create a verification code that expires in 10 minutes."""
        # --- ✅ Delete old code if it exists ---
        existing_record = await super().get_one(user_id=user_id)
        if existing_record:
            await super().delete_by_filter(user_id=user_id)

        # --- ✅ Generate new code ---
        code = GeneratorManager.generate_digits_code(6)
        expires_at = GeneratorManager.expires_at(10)
        result = await super().create(
            user_id=user_id,
            code=code,
            expires_at=expires_at
        )
        return code

    async def get_user_verification_code(self, user_id: str):
        """Retrieve the user's active verification code record."""
        record = await super().get_one(user_id=user_id)
        return record

    async def delete_verification_code(self, user_id: str):
        """Delete user's verification code (used after success or timeout)."""
        result = await super().delete_by_filter(user_id=user_id)
        return result


    async def verify_code(self, user_id: str, code: str):
        """Check if the provided verification code is valid and not expired."""
        record = await self.get_user_verification_code(user_id)
        if not record:
            Exceptions.not_found("No verification code found for this user")

        if record.expires_at.tzinfo is None:
            record.expires_at = record.expires_at.replace(tzinfo=timezone.utc)
        # Check if expired
        if datetime.now(timezone.utc) > record.expires_at:
            await self.delete_verification_code(user_id)
            Exceptions.bad_request("Verification code has expired")

        # Check if code matches
        if record.code != code:
            Exceptions.bad_request("Invalid verification code")
        await self.delete_verification_code(user_id)
        return {"message": "Verification successful"}

verification_code_crud = VerificationCodeCrud()
