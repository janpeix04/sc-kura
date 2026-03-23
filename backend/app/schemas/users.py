from sqlmodel import SQLModel, Field
from pydantic import EmailStr


class UserBase(SQLModel):
    first_name: str = Field(nullable=False, min_length=2, max_length=50)
    last_name: str = Field(nullable=False, min_length=2, max_length=50)
    emial: EmailStr = Field(nullable=False, unique=True, max_length=255)
    is_verified: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
