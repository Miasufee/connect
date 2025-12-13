from starlette.responses import JSONResponse

from app.core.response.exceptions import Exceptions
from app.core.response.success import Success
from app.core.token_manager import TokenManager
from app.crud import user_crud
from app.crud.user_cruds.verification_code_crud import verification_code_crud
from app.schemas.user.user_auth_schema import UserCreate, UserOut, UserLogin


class UserService:
    """Service class for handling regular user registration and login."""

    @staticmethod
    async def create_user(user_data: UserCreate) -> JSONResponse:
        """
        Create a regular user and send a verification code via email.

        Args:
            user_data (UserCreate): Input schema containing user email and other info.

        Returns:
            Success: Response with created user info.
        """
        existing_user = await user_crud.get_by_email(user_data.email)
        if existing_user:
            raise Exceptions.email_exist()

        new_user = await user_crud.create(email=user_data.email)

        # Generate verification code and send email
        _ = await verification_code_crud.create_verification_code(str(new_user.id))

        user_response = UserOut.model_validate(new_user.model_dump())
        return Success.account_created(user=user_response)

    @staticmethod
    async def login_user(user_data: UserLogin) -> JSONResponse:
        """
        Login a regular user via email and verification code.

        Args:
            user_data (UserLogin): User login input containing email and optional verification code.

        Returns:
            Success: Response containing access and refresh tokens, or info about a send verification code.
        """
        db_user = await user_crud.get_by_email(user_data.email)
        if not db_user:
            raise Exceptions.not_found("Email not registered")
        if not db_user.is_email_verified:
            raise Exceptions.not_verified()

        # If verification code is provided, verify and login
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
        return Success.ok(f"Verification code sent to {db_user.email} {code_record}")

user_service = UserService()