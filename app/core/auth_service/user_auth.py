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

    if not db_user:
        raise Exceptions.not_found("Email not register")
    if not db_user.is_email_verified:
        raise Exceptions.not_verified()
    # ===== Step 1: If verification code is provided, verify it =====
    if user_data.verification_code:
        record = await verification_code_crud.verify_code(db_user.id, user_data.verification_code)
        if not record:
            raise Exceptions.invalid_verification_code()
        # If valid — update login timestamp and generate tokens
        await user_crud.update_last_login(db_user.id)
        access_token, refresh_token = await TokenManager.generate_token_pair(db_user)
        # Return full login success response with cookies + data
        user_response = UserResponse.model_validate(db_user.model_dump())
        return Success.login_success(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_response
        )

    # ===== Step 2: If no code, send a new one =====
    code_record = await verification_code_crud.create_verification_code(db_user.id)
    send_verification_to_email(db_user, code_record)
    return Success.ok(f"Verification code sent to {db_user.email}")
