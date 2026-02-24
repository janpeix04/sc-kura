import uuid
from datetime import datetime
from typing import List

from enum import Enum
from sqlmodel import SQLModel, Field, BigInteger, Column


class FileFolderStatus(str, Enum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    FAILED = "failed"
    DELETED = "deleted"


class FileBase(SQLModel):
    original_name: str = Field(min_length=2, max_length=255)
    stored_name: str = Field(min_length=2, max_length=255)
    path: str = Field(nullable=False, min_length=1)

    size: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    mime_type: str = Field(nullable=False, max_length=255)
    checksum: str = Field(min_length=2, max_length=255)

    status: FileFolderStatus = Field(default=FileFolderStatus.PENDING, nullable=False)


class FileCreate(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    original_name: str
    stored_name: str
    path: str
    size: int
    mime_type: str
    checksum: str = ""
    status: FileFolderStatus
    user_id: uuid.UUID
    folder_id: uuid.UUID


class FolderBase(SQLModel):
    original_name: str = Field(min_length=2, max_length=255)
    stored_name: str | None = Field(default=None, min_length=2, max_length=255)
    path: str = Field(nullable=False, min_length=1)
    deleted_path: str | None = Field(default=None, nullable=True)

    size: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    mime_type: str = Field(default="directory")

    status: FileFolderStatus = Field(default=FileFolderStatus.PENDING, nullable=False)


class FolderCreate(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    original_name: str
    stored_name: str | None = None
    path: str
    size: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    mime_type: str = "directory"
    status: FileFolderStatus
    user_id: uuid.UUID | None = None
    parent_id: uuid.UUID | None = None


class FileFolderPublic(SQLModel):
    id: uuid.UUID
    name: str
    size: int
    type: str
    path: str
    lastModified: datetime


class AvailableSpace(SQLModel):
    total: int
    used: int
    free: int


class UploadFiles(SQLModel):
    uploaded: List[str]
    errors: List[str]
    total_uploaded: int
    total_errors: int
