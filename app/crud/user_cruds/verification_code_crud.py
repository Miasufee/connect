
from beanie import PydanticObjectId

from app.crud.crud_base import CrudBase
from app.models import utc_now
from app.models.user_models import VerificationCode
from app.core.response.exceptions import Exceptions
from app.core.utils.generator import GeneratorManager


class VerificationCodeCrud(CrudBase[VerificationCode]):
    def __init__(self):
        super().__init__(VerificationCode)

    async def create_verification_code(self, user_id: PydanticObjectId) -> str:
        # Delete any existing code
        await super().delete_by_filter(user_id=user_id)

        code = GeneratorManager.generate_digits_code(6)
        expires_at = GeneratorManager.expires_at(10)

        await super().create(
            user_id=user_id,
            code=code,
            expires_at=expires_at,
        )
        return code

    async def get_user_verification_code(self, user_id: PydanticObjectId):
        return await super().get_one(user_id=user_id)

    async def delete_verification_code(self, user_id: PydanticObjectId):
        return await super().delete_by_filter(user_id=user_id)

    async def verify_code(self, user_id: PydanticObjectId, code: str):
        record = await self.get_user_verification_code(user_id)

        if not record:
            raise Exceptions.not_found("No verification code found")

        now = utc_now()

        if now >= record.expires_at:
            await self.delete_verification_code(user_id)
            raise Exceptions.bad_request("Verification code has expired")

        if record.code != code:
            raise Exceptions.bad_request("Invalid verification code")

        await self.delete_verification_code(user_id)
        return {"message": "Verification successful"}


verification_code_crud = VerificationCodeCrud()