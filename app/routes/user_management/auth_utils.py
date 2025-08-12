from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    CurrentUser,
    AdminUser,
    SuperAdminUser,
    SuperUser
)
from app.core.database import get_async_db
from app.core.utils.generate import VerificationManager
from app.core.utils.response.exceptions import Exceptions
from app.core.utils.response.success import Success
from app.crud.user_management import user_crud
from app.schemas.user_schema import UserEmailVerification, UserEmail

router = APIRouter()


@router.get("/get/verification/code")
async def _get_verification_code(
    user_email: UserEmail,
    db: AsyncSession = Depends(get_async_db)
):
    db_user = await user_crud.get_by_email(db, user_email.email)
    if not db_user:
        raise Exceptions.email_not_registered()

    verification_code = await VerificationManager.generate_code(
        user_id=db_user.id,
        db=db,
    )
    return Success.verification_code_sent(verification_code)


@router.post("/verify/email/")
async def _verify_email(
    payload: UserEmailVerification,
    db: AsyncSession = Depends(get_async_db)
):
    db_user = await user_crud.get_by_email(db, email=payload.email)
    if not db_user:
        raise Exceptions.email_not_registered()

    if not await VerificationManager.verify_code(
        user_id=db_user.id,
        code=payload.verification_code,
        db=db
    ):
        raise Exceptions.invalid_verification_code()

    db_user.is_email_verified = True
    await db.commit()
    return Success.email_verified()


@router.post("/verify/phone/number/")
async def _verify_phone_number():
    pass


@router.post("/approve/admin/user/")
async def _approve_admin():
    pass


@router.get("/me")
async def get_me(current_user: CurrentUser):
    return {
        "email": current_user.email,
        "role": current_user.role.value
    }


@router.get("/admin-panel")
async def admin_panel(admin_user: AdminUser):
    return {"msg": f"Welcome Admin {admin_user.email}"}


@router.get("/super-admin-panel")
async def super_admin_panel(super_admin_user: SuperAdminUser):
    return {"msg": f"Hello SuperAdmin {super_admin_user.email}"}


@router.get("/superuser-panel")
async def superuser_panel(superuser: SuperUser):
    return {"msg": f"Hello Superuser {superuser.email}"}
