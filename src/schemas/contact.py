from datetime import date

from pydantic import BaseModel, EmailStr, Field

from src.schemas.user import UserResponse

class ContactSchema(BaseModel):
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=9, max_length=15)
    birthday: date
    description: str = Field(min_length=5, max_length=250)


class ContactUpdateSchema(BaseModel):
    first_name: str | None = Field(min_length=3, max_length=50, default=None)
    last_name: str | None = Field(min_length=3, max_length=50, default=None)
    email: EmailStr | None = None
    phone: str | None = Field(min_length=9, max_length=15, default=None)
    birthday: date | None = None
    description: str | None = Field(min_length=5, max_length=250, default=None)


class ContactResponse(BaseModel):
    id: int = 1
    first_name: str
    last_name: str
    email: str
    phone: str
    birthday: date
    description: str
    user: UserResponse | None

    class Config:
        from_attributes = True