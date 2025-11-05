from app.core.email_service import send_verification_to_email
from app.core.response.exceptions import Exceptions
from app.core.response.success import Success
from app.core.token_manager import TokenManager
from app.crud import user_crud
from app.crud.verification_code_crud import verification_code_crud
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin


async def user_create_service(user_data: UserCreate):
    """Create a regular user and send a verification code."""
    existing_user = await user_crud.get_by_email(user_data.email)
    if existing_user:
        raise Exceptions.email_exist()
    new_user = await user_crud.create(email=user_data.email)
    code_record = await verification_code_crud.create_verification_code(str(new_user.id))
    send_verification_to_email(new_user, code_record)
    user_response = UserResponse.model_validate(new_user.model_dump())
    return Success.account_created(user=user_response)


async def user_login_service(user_data: UserLogin):
    """Login user via email + verification code flow (for regular users only)."""
    db_user = await user_crud.get_by_email(user_data.email)

    if not db_user.is_email_verified:
        raise Exceptions.not_verified()

    if user_data.verification_code:
        verified = await verification_code_crud.verify_code(
            db_user.id, user_data.verification_code
        )
        if verified:
            await user_crud.update_last_login(db_user.id)
            return await TokenManager.generate_token_pair(db_user)

        raise Exceptions.invalid_verification_code()

    await verification_code_crud.create_verification_code(db_user.id)
    return Success.ok("Verification code sent to email")

