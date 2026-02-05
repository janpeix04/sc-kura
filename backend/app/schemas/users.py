from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    username: str = Field(nullable=False, min_length=2, max_length=255)
    is_verified: bool = Field(default=False)
    is_superuser: bool = Field(default=False)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=255)
