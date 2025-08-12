from typing import List, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CrudBase
from app.models.user.user import Address
from app.schemas.user_schema.address_schemas import AddressCreate, AddressUpdate, AddressResponse


class AddressCrud(CrudBase[Address]):
    def __init__(self):
        super().__init__(Address)

    async def get_user_addresses(self, db: AsyncSession, user_id: int) -> Sequence[Address]:
        """Get all addresses for a user"""
        return await self.get_multi(db, user_id=user_id)

    async def create_address(
        self,
        db: AsyncSession,
        user_id: int,
        region: str,
        state: str,
        city: str,
        postal_code: str,
        street: str,
        house_number: str,
        street2: Optional[str] = None
    ) -> Address:
        """Create a new address"""
        return await self.create(
            db,
            user_id=user_id,
            region=region,
            state=state,
            city=city,
            postal_code=postal_code,
            street=street,
            house_number=house_number,
            street2=street2
        )

    async def update_address(self, db: AsyncSession, address_id: int, **kwargs) -> Address:
        """Update an address"""
        return await self.update(db, obj_id=address_id, **kwargs)

    async def get_addresses_by_city(self, db: AsyncSession, city: str) -> Sequence[Address]:
        """Get addresses by city"""
        return await self.get_multi(db, city=city)

    async def get_addresses_by_region(self, db: AsyncSession, region: str) -> Sequence[Address]:
        """Get addresses by region"""
        return await self.get_multi(db, region=region)

    async def delete_user_addresses(self, db: AsyncSession, user_id: int) -> None:
        """Delete all addresses for a user"""
        await self.delete(db, user_id=user_id)

    async def get_full_address(self, db: AsyncSession, address_id: int) -> Optional[str]:
        """Get formatted full address"""
        address = await self.get(db, obj_id=address_id)
        if address:
            parts = [
                address.house_number,
                address.street,
                address.street2,
                address.city,
                address.state,
                address.region,
                address.postal_code
            ]
            return ", ".join(filter(None, parts))
        return None

    async def create_address_with_schema(
        self,
        db: AsyncSession,
        address_create: AddressCreate
    ) -> AddressResponse:
        """Create address using schema"""
        address = await self.create(db, **address_create.model_dump())
        return AddressResponse.model_validate(address)

    async def update_address_with_schema(
        self,
        db: AsyncSession,
        address_id: int,
        address_update: AddressUpdate
    ) -> AddressResponse:
        """Update address using schema"""
        update_data = address_update.model_dump(exclude_unset=True)
        address = await self.update(db, obj_id=address_id, **update_data)
        return AddressResponse.model_validate(address)

    async def get_user_addresses_with_schema(
        self,
        db: AsyncSession,
        user_id: int
    ) -> List[AddressResponse]:
        """Get user addresses with schema response"""
        addresses = await self.get_user_addresses(db, user_id)
        return [AddressResponse.model_validate(address) for address in addresses]


address_crud = AddressCrud()
