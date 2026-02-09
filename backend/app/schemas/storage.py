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
