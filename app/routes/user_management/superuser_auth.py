from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.crud.user_management.superuser_crud import super_user_crud
from app.schemas.user_schema import SuperUserCreate, SuperUserLogin

router = APIRouter()

@router.post("/create")
async def _create_superuser(payload: SuperUserCreate, db: AsyncSession = Depends(get_async_db)):
    return await super_user_crud.create_superuser(
        db=db,
        email=payload.email,
        password=payload.hashed_password,
        secret_key=payload.superuser_secret_key
    )


@router.post("/login")
async def _Login_superuser(payload: SuperUserLogin, db: AsyncSession = Depends(get_async_db)):
    print(payload.email)
    print(payload.hashed_password)
    print(payload.unique_id)
    return await super_user_crud.login_superuser(
        db=db, email=payload.email,
        password=payload.hashed_password,
        unique_id=payload.unique_id
    )