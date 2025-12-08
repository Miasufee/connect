from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class PaginatedResponse(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool
