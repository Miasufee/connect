from typing import Optional, Any, Coroutine

from starlette.responses import JSONResponse

from app.core.response.exceptions import Exceptions
from app.core.response.success import Success
from app.crud import user_crud
from app.crud.user_cruds.verification_code_crud import verification_code_crud


class VerificationService:
    """Handles verification code generation and email verification."""

    @staticmethod
    async def generate_verification_code(user_email: str) -> JSONResponse:
        """
        Generate and store a new verification code for a user.

        Args:
            user_email (str): User email address.

        Returns:
            Success: Contains the verification code to send via email.
        """
        db_user = await user_crud.get_by_email(user_email)
        if not db_user:
            raise Exceptions.email_not_registered()

        await verification_code_crud.delete_verification_code(str(db_user.id))
        code_record = await verification_code_crud.create_verification_code(str(db_user.id))

        return Success.ok(
            message="Verification code generated successfully",
            verification_code=code_record
        )

    @staticmethod
    async def verify_email(user_email: str, code: str) -> JSONResponse:
        """
        Verify user's email using the provided verification code.

        Args:
            user_email (str): User email.
            code (str): Verification code sent to user.

        Returns:
            Success: Confirmation of successful verification.
        """
        db_user = await user_crud.get_by_email(user_email)
        if not db_user:
            raise Exceptions.email_not_registered()

        if db_user.is_email_verified:
            raise Exceptions.already_verified()

        valid = await verification_code_crud.verify_code(db_user.id, code)
        if not valid:
            raise Exceptions.invalid_verification_code()

        db_user.is_email_verified = True
        await db_user.save()
        return Success.ok(message="Email verified successfully")


verification_service = VerificationService()