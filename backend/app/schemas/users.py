import uuid
from typing import Annotated

from pydantic import EmailStr
from sqlmodel import Field, SQLModel
from fastapi import Form


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    username: str = Field(nullable=False, min_length=2, max_length=255)
    is_verified: bool = Field(default=False)
    is_superuser: bool = Field(default=False)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=255)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    username: str = Field(min_length=2, max_length=255)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str = Field(min_length=8, max_length=40)
    username: str | None = Field(default=None, min_length=2, max_length=255)


class UserUpdateMe(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    username: str | None = Field(default=None, min_length=2, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class UserPublic(UserBase):
    id: uuid.UUID
    is_superuser: bool


class UserInfo(SQLModel):
    id: uuid.UUID
    email: str
    username: str


class UsersPublic(UserPublic):
    data: list[UserPublic]
    count: int


class UserRegisterForm(UserRegister):
    @classmethod
    def as_form(
        cls,
        email: Annotated[EmailStr, Form()],
        password: Annotated[str, Form()],
        username: Annotated[str, Form()],
    ):
        return cls(email=email, password=password, username=username)
