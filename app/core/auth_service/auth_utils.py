from app.core.response.exceptions import Exceptions
from app.core.response.success import Success
from app.crud import user_crud
from app.crud.verification_code_crud import verification_code_crud


async def get_verification(user_email):
    """
    Generate and store a new verification code for the user.
    Returns the code so it can be sent by email.
    """
    db_user = await user_crud.get_by_email(user_email)
    if not db_user:
        raise Exceptions.email_not_registered()

    # Optional: Delete any old verification code for the same user
    await verification_code_crud.delete_verification_code(str(db_user.id))

    # Create a new one
    code_record = await verification_code_crud.create_verification_code(str(db_user.id))

    # Return the code (for testing or sending via email)
    return Success.ok(
        message="Verification code generated successfully",
        data={"code": code_record.code}
    )


async def verify_email(user_email, code: str):
    """
    Verify the user's email by matching their verification code.
    """
    db_user = await user_crud.get_by_email(user_email)
    if not db_user:
        raise Exceptions.email_not_registered()

    if db_user.is_email_verified:
        raise Exceptions.already_verified()

    # Validate verification code
    verification_result = await verification_code_crud.verify_code(db_user.id, code)

    if not verification_result:
        raise Exceptions.invalid_verification_code()

    # Mark email as verified
    db_user.is_email_verified = True
    await db_user.save()

    return Success.ok(message="Email verified successfully")
