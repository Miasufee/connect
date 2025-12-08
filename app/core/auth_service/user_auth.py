from app.core.services.email.service import email_service
from app.core.response.exceptions import Exceptions
from app.core.response.success import Success
from app.core.token_manager import TokenManager
from app.crud import user_crud
from app.crud.user_cruds.verification_code_crud import verification_code_crud
from app.schemas.user.user_auth_schema import UserCreate, UserOut, UserLogin



async def user_create_service(user_data: UserCreate):
    """Create a regular user and send a verification code."""
    existing_user = await user_crud.get_by_email(user_data.email)
    if existing_user:
        raise Exceptions.email_exist()
    new_user = await user_crud.create(email=user_data.email)
    code_record = await verification_code_crud.create_verification_code(str(new_user.id))
    await email_service.send_verification_code_email(new_user.email, code_record)
    user_response = UserOut.model_validate(new_user.model_dump())
    return Success.account_created(user=user_response)


async def user_login_service(user_data: UserLogin):
    """Login user via email + verification code flow (for regular users only)."""
    db_user = await user_crud.get_by_email(user_data.email)

    if not db_user:
        raise Exceptions.not_found("Email not registered")
    if not db_user.is_email_verified:
        raise Exceptions.not_verified()
    if user_data.verification_code:
        record = await verification_code_crud.verify_code(db_user.id, user_data.verification_code)
        if not record:
            raise Exceptions.invalid_verification_code()
        await user_crud.update_last_login(db_user.id)
        access_token, refresh_token = await TokenManager.generate_token_pair(db_user)
        user_response = UserOut.model_validate(db_user.model_dump())
        return Success.login_success(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_response
        )
    # If no verification code provided, send a new one
    code_record = await verification_code_crud.create_verification_code(str(db_user.id))
    await email_service.send_verification_code_email(db_user.email, code_record)
    return Success.ok(f"Verification code sent to {db_user.email} {code_record}")

