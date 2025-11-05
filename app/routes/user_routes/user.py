from datetime import datetime

from fastapi import APIRouter


from app.crud.user_crud import user_crud


router = APIRouter(prefix="/users", tags=["users"])

async def create_user():
    pass