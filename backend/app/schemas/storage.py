import uuid
from datetime import datetime

from enum import Enum
from sqlmodel import SQLModel, Field


class FileStatus(str, Enum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    FAILED = "failed"
    DELETED = "deleted"


class FileBase(SQLModel):
    original_name: str = Field(min_length=2, max_length=255)
    stored_name: str = Field(min_length=2, max_length=255)
    path: str = Field(nullable=False, min_length=1)

    size: int = Field(nullable=False)
    mime_type: str = Field(nullable=False, max_length=255)
    checksum: str = Field(min_length=2, max_length=255)

    status: FileStatus = Field(default=FileStatus.PENDING, nullable=False)


class FileCreate(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    original_name: str
    stored_name: str
    path: str
    size: int
    mime_type: str
    checksum: str = ""
    status: FileStatus
    user_id: uuid.UUID
    folder_id: uuid.UUID


class FolderBase(SQLModel):
    original_name: str = Field(min_length=2, max_length=255)
    stored_name: str | None = Field(default=None, min_length=2, max_length=255)
    path: str = Field(nullable=False, min_length=1)

    size: int = Field(default=0, nullable=False)
    mime_type: str = Field(default="directory")


class FolderCreate(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    original_name: str
    stored_name: str | None = None
    path: str
    size: int = 0
    mime_type: str = "directory"
    user_id: uuid.UUID | None = None
    parent_id: uuid.UUID | None = None


class FileFolderPublic(SQLModel):
    id: uuid.UUID
    name: str
    size: int
    type: str
    path: str
    lastModified: datetime
