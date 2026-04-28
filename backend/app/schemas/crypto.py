import uuid

from sqlmodel import SQLModel, Field, Column, BigInteger
from app.schemas.storage import FileStatus, FolderStatus


class EncryptedFolderBase(SQLModel):
    encrypted_key: str = Field(nullable=False)
    iv: str = Field(nullable=False)

    encrypted_name: str = Field(min_length=1)

    type: str = Field(default="directory")
    size: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))
    status: FolderStatus = Field(default=FolderStatus.UPLOADED, nullable=False)


class EncryptedFileBase(SQLModel):
    encrypted_key: str = Field(nullable=False)
    iv: str = Field(nullable=False)

    encrypted_name: str = Field(min_length=1)
    encrypted_name_iv: str = Field(nullable=False)

    storage_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    size: int = Field(default=0, sa_column=Column(BigInteger, nullable=False))

    status: FileStatus = Field(default=FileStatus.PENDING, nullable=False)
