import uuid
from datetime import datetime

from enum import Enum
from pydantic import BaseModel

from sqlmodel import SQLModel, Field, Column, BigInteger


class FolderStatus(str, Enum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    FAILED = "failed"
    DELETED = "deleted"


class FolderBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    location: str = Field(min_length=1, max_length=255)
    type: str = Field(default="directory")
    size: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    owner: str = Field(min_length=2, max_length=255)
    status: FolderStatus = Field(default=FolderStatus.PENDING, nullable=False)


class FolderCreate(FolderBase):
    status: FolderStatus = Field(default=FolderStatus.UPLOADED)
    parent_id: uuid.UUID | None = Field(default=None, nullable=True)
    user_id: uuid.UUID


class FolderPublic(BaseModel):
    id: uuid.UUID
    name: str
    location: str
    type: str
    size: int
    owner: str
    modified_at: datetime
    opened_at: datetime
    created_at: datetime
    parent_id: uuid.UUID | None


class FolderUpdate(SQLModel):
    name: str | None = Field(default=None, nullable=True)


class NewFolder(SQLModel):
    name: str = Field(min_length=1, max_length=255)


class Breadcrumbs(BaseModel):
    folder_name: str
    folder_id: uuid.UUID


class FileStatus(str, Enum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    FAILED = "failed"
    DELETED = "deleted"


class FileBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    location: str = Field(min_length=1, max_length=255)
    path: str = Field(nullable=False)
    type: str = Field(nullable=False)
    size: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    owner: str = Field(min_length=2, max_length=255)
    status: FileStatus = Field(default=FileStatus.PENDING, nullable=False)


class FilePublic(BaseModel):
    id: uuid.UUID
    name: str
    location: str
    type: str
    size: int
    owner: str
    modified_at: datetime
    opened_at: datetime
    created_at: datetime
    folder_id: uuid.UUID | None
