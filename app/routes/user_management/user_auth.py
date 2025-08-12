from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.utils.generate import VerificationManager
from app.core.utils.response.exceptions import Exceptions
from app.core.utils.response.success import Success
from app.core.utils.token_manager import token_manager
from app.crud.user_management import user_crud
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin, UserEmailVerification


router = APIRouter()

@router.post("/create", response_model=UserResponse)
async def create_user_(user_data: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """create regular user with email"""
    existing_user = await user_crud.get_by_email(db, user_data.email)
    if existing_user:
        raise Exceptions.email_exist()
    new_user = await user_crud.create(db, email=user_data.email)
    response = UserResponse.model_validate(new_user)
    return Success.account_created(response)


@router.post("/login")
async def login_user(login_data: UserLogin, db: AsyncSession = Depends(get_async_db)):
    """
    Two-step login process:
    1. First request with email: generates and returns verification code
    2. Second request with email + verification code: returns access/refresh tokens
    """
    db_user = await user_crud.get_by_email(db, login_data.email)
    if not db_user:
        raise Exceptions.email_not_registered(detail="Email not registered, please sign up")

    # Step 2: If verification code provided, validate it
    if login_data.verification_code:
        # Use the new verification method
        if not await VerificationManager.verify_code(
            user_id=db_user.id,
            code=login_data.verification_code,
            db=db
        ):
            raise Exceptions.invalid_verification_code()

        # Generate token pair
        tokens, expires = await token_manager.create_tokens(db, db_user)

        return Success.login_success(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            user=UserResponse.model_validate(db_user),
        )
    # Step 3: If no verification code, generate and return one
    verification_code = await VerificationManager.generate_code(
        user_id=db_user.id,
        db=db,
        code_length=6,
        expiry_minutes=10
    )
    return Success.verification_code_sent(verification_code=verification_code)

@router.get("/get/verification/code")
async def _get_verification_code(user_email: UserEmailVerification, db: AsyncSession = Depends(get_async_db)):
    db_user = await user_crud.get_by_email(db, user_email.email)
    if not db_user:
        raise Exceptions.email_not_registered()
    verification_code = await VerificationManager.generate_code(
        user_id=db_user.id,
        db=db,
    )
    return Success.verification_code_sent(verification_code)

@router.post("/verify/email/")
async def _verify_email():
    pass