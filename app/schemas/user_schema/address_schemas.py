from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class AddressBase(BaseModel):
    region: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    city: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=20)
    street: str = Field(..., max_length=255)
    street2: Optional[str] = Field(None, max_length=255)
    house_number: str = Field(..., max_length=20)


class AddressCreate(AddressBase):
    user_id: int


class AddressUpdate(BaseModel):
    region: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    street: Optional[str] = Field(None, max_length=255)
    street2: Optional[str] = Field(None, max_length=255)
    house_number: Optional[str] = Field(None, max_length=20)


class AddressResponse(AddressBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    @property
    def full_address(self) -> str:
        parts = [
            self.house_number,
            self.street,
            self.street2,
            self.city,
            self.state,
            self.region,
            self.postal_code
        ]
        return ", ".join(filter(None, parts))
