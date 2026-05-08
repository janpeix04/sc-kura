import uuid

from datetime import datetime
from pydantic import BaseModel

from sqlmodel import SQLModel, Field, Column, BigInteger

from app.schemas.storage import FileStatus, FolderStatus


class EncryptedFolderBase(SQLModel):
    encrypted_key: str = Field(nullable=False)
    iv: str = Field(nullable=False)

    encrypted_name: str = Field(min_length=1)

    type: str = Field(default="directory")
    size: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    status: FolderStatus = Field(default=FolderStatus.PENDING, nullable=False)


class EncryptedFolderCreate(EncryptedFolderBase):
    status: FolderStatus = Field(default=FolderStatus.UPLOADED)
    parent_id: uuid.UUID | None = None
    user_id: uuid.UUID


class EncryptedFolderPublic(BaseModel):
    id: uuid.UUID
    encrypted_key: str
    iv: str
    encrypted_name: str
    type: str = "directory"
    size: int
    created_at: datetime
    parent_id: uuid.UUID | None


class EncryptedFolderRename(SQLModel):
    iv: str = Field(nullable=False)
    encrypted_name: str = Field(nullable=False)


class NewEncryptedFolder(BaseModel):
    encrypted_key: str
    iv: str
    encrypted_name: str


class EncryptedFileBase(SQLModel):
    encrypted_key: str = Field(nullable=False)
    iv: str = Field(nullable=False)

    encrypted_name: str = Field(min_length=1)
    encrypted_name_iv: str = Field(nullable=False)

    storage_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    size: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))

    status: FileStatus = Field(default=FileStatus.PENDING, nullable=False)


class EncryptedFileCreate(EncryptedFileBase):
    status: FileStatus = Field(default=FileStatus.UPLOADED)
    parent_id: uuid.UUID
    user_id: uuid.UUID


class EncryptedFilePublic(BaseModel):
    id: uuid.UUID
    encrypted_key: str = Field(nullable=False)
    iv: str = Field(nullable=False)
    encrypted_name: str = Field(min_length=1)
    encrypted_name_iv: str = Field(nullable=False)
    size: int
    created_at: datetime
    parent_id: uuid.UUID | None


class EncryptedFileRename(SQLModel):
    iv: str = Field(nullable=False)
    encrypted_name: str = Field(nullable=False)


class CryptoBreadcrumbs(BaseModel):
    folder_encrypted_key: str
    folder_iv: str
    folder_encrypted_name: str
    folder_id: uuid.UUID
