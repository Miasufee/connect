from typing import Optional, List, Any, Coroutine, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_
from app.crud.base import CrudBase
from app.models.user.user import PhoneNumber
from app.schemas.user_schema import PhoneNumberCreate, PhoneNumberUpdate, PhoneNumberResponse


class PhoneNumberCrud(CrudBase[PhoneNumber]):
    def __init__(self):
        super().__init__(PhoneNumber)

    async def get_by_phone(
        self, 
        db: AsyncSession, 
        country_code: str, 
        phone_number: str
    ) -> Optional[PhoneNumber]:
        """Get phone number by country code and number"""
        return await self.get(db, country_code=country_code, phone_number=phone_number)

    async def get_user_phone_numbers(self, db: AsyncSession, user_id: int) -> Sequence[Any]:
        """Get all phone numbers for a user"""
        return await self.get_multi(db, user_id=user_id)

    async def create_phone_number(
        self,
        db: AsyncSession,
        user_id: int,
        country_code: str,
        phone_number: str,
        is_verified: bool = False
    ) -> PhoneNumber:
        """Create a new phone number"""
        return await self.create(
            db,
            user_id=user_id,
            country_code=country_code,
            phone_number=phone_number,
            is_verified=is_verified
        )

    async def verify_phone_number(self, db: AsyncSession, phone_id: int) -> PhoneNumber:
        """Mark phone number as verified"""
        return await self.update(db, obj_id=phone_id, is_verified=True)

    async def get_verified_phone_numbers(self, db: AsyncSession, user_id: int) -> List[PhoneNumber]:
        """Get verified phone numbers for a user"""
        return await self.get_multi(db, user_id=user_id, is_verified=True)

    async def phone_exists(self, db: AsyncSession, country_code: str, phone_number: str) -> bool:
        """Check if phone number already exists"""
        return await self.exists(db, country_code=country_code, phone_number=phone_number)

    async def delete_user_phone_numbers(self, db: AsyncSession, user_id: int) -> None:
        """Delete all phone numbers for a user"""
        await self.delete(db, user_id=user_id)

    async def create_phone_with_schema(
        self,
        db: AsyncSession,
        phone_create: PhoneNumberCreate
    ) -> PhoneNumberResponse:
        """Create phone number using schema"""
        phone = await self.create(db, **phone_create.model_dump())
        return PhoneNumberResponse.model_validate(phone)

    async def update_phone_with_schema(
        self,
        db: AsyncSession,
        phone_id: int,
        phone_update: PhoneNumberUpdate
    ) -> PhoneNumberResponse:
        """Update phone number using schema"""
        update_data = phone_update.model_dump(exclude_unset=True)
        phone = await self.update(db, obj_id=phone_id, **update_data)
        return PhoneNumberResponse.model_validate(phone)

    async def get_user_phones_with_schema(
        self,
        db: AsyncSession,
        user_id: int
    ) -> List[PhoneNumberResponse]:
        """Get user phone numbers with schema response"""
        phones = await self.get_user_phone_numbers(db, user_id)
        return [PhoneNumberResponse.model_validate(phone) for phone in phones]


phone_number_crud = PhoneNumberCrud()
