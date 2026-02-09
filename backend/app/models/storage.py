import uuid
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime, timezone

from sqlmodel import Field, DateTime, Relationship
from app.schemas.storage import (
    FileBase,
    FolderBase,
    StorageMetadataFieldBase,
    StorageMetadataFieldLinkBase,
)

if TYPE_CHECKING:
    from app.models.users import User


class File(FileBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    user: "User" = Relationship(back_populates="files")

    folder_id: uuid.UUID = Field(foreign_key="folder.id", ondelete="CASCADE")
    folder: "Folder" = Relationship(back_populates="files")

    metadataFieldLinks: List["StorageMetadataFieldLink"] = Relationship(
        back_populates="file"
    )


class Folder(FolderBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    files: List["File"] = Relationship(back_populates="folder")

    user_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    user: "User" = Relationship(back_populates="folders")

    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="folder.id")
    parent: Optional["Folder"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Folder.id"}
    )

    children: List["Folder"] = Relationship(back_populates="parent")


class StorageMetadataField(StorageMetadataFieldBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    user_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    user: "User" = Relationship(back_populates="storagemetadatafields")

    storagemetadatafieldlinks: List["StorageMetadataFieldLink"] = Relationship(
        back_populates="metadataField"
    )


class StorageMetadataFieldLink(StorageMetadataFieldLinkBase, table=True):
    value_str: str | None = Field(default=None)
    value_bool: bool | None = Field(default=None)
    value_int: int | None = Field(default=None)
    value_float: float | None = Field(default=None)

    file_id: uuid.UUID = Field(
        foreign_key="file.id", primary_key=True, ondelete="CASCADE"
    )
    file: "File" = Relationship(back_populates="metadataFieldLinks")

    metadata_id: uuid.UUID = Field(
        foreign_key="storagemetadatafield.id", primary_key=True, ondelete="CASCADE"
    )
    metadataField: "StorageMetadataField" = Relationship(
        back_populates="storagemetadatafieldlinks"
    )
