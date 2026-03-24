import uuid

from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class UserBase(SQLModel):
    first_name: str = Field(nullable=False, min_length=2, max_length=50)
    last_name: str = Field(nullable=False, min_length=2, max_length=50)
    email: EmailStr = Field(nullable=False, unique=True, max_length=255)
    is_verified: bool = Field(default=False)
    is_superuser: bool = Field(default=False)


class UserCreate(UserBase):
    password: str = Field(nullable=False, min_length=8)


class UserRegister(SQLModel):
    first_name: str = Field(nullable=False, min_length=2, max_length=50)
    last_name: str = Field(nullable=False, min_length=2, max_length=50)
    email: EmailStr = Field(nullable=False, unique=True, max_length=255)
    password: str = Field(nullable=False, min_length=8)


class UserPublic(UserBase):
    id: uuid.UUID


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str = Field(min_length=8, max_length=40)
    username: str | None = Field(default=None, min_length=2, max_length=255)
