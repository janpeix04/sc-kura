import uuid

from pydantic import BaseModel

from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class UserBase(SQLModel):
    first_name: str = Field(nullable=False, min_length=2, max_length=50)
    last_name: str = Field(nullable=False, min_length=2, max_length=50)
    email: EmailStr = Field(nullable=False, unique=True, max_length=255)
    is_verified: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    has_seen_personal_vault: bool = Field(default=False)


class UserCreate(UserBase):
    password: str = Field(nullable=False, min_length=8)


class UserRegister(SQLModel):
    first_name: str = Field(nullable=False, min_length=2, max_length=50)
    last_name: str = Field(nullable=False, min_length=2, max_length=50)
    email: EmailStr = Field(nullable=False, unique=True, max_length=255)
    password: str = Field(nullable=False, min_length=8)


class UserPublic(UserBase):
    id: uuid.UUID


class UserUpdate(SQLModel):
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    password: str | None = Field(default=None)
    has_seen_personal_vault: bool | None = Field(default=None)


class UserKeyBase(SQLModel):
    public_key: str = Field(nullable=False)
    encrypted_private_key: str = Field(nullable=False)
    encrypted_private_key_recovery: str = Field(nullable=False)
    iv: str = Field(nullable=False)
    iv_recovery: str = Field(nullable=False)
    pbkdf2_salt: str = Field(nullable=False)


class UserKeyCreate(UserKeyBase):
    user_id: uuid.UUID


class UserKeyPublic(BaseModel):
    public_key: str
    encrypted_private_key: str
    encrypted_private_key_recovery: str
    iv: str
    iv_recovery: str
    pbkdf2_salt: str
