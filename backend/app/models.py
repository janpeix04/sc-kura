import uuid
from typing import List, Optional
from datetime import datetime, timezone

from sqlmodel import Field, DateTime, Relationship
from app.schemas.storage import (
    FileBase,
    FolderBase,
)
from app.schemas.users import UserBase


# -----------------------------------------------------------
#                           USER MODEL
# -----------------------------------------------------------
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    files: List["File"] = Relationship(back_populates="user")
    folders: List["Folder"] = Relationship(back_populates="user")


# -----------------------------------------------------------
#                           FILE MODEL
# -----------------------------------------------------------
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

    folder_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="folder.id", ondelete="CASCADE"
    )
    folder: "Folder" = Relationship(back_populates="files")


# -----------------------------------------------------------
#                           FOLDER MODEL
# -----------------------------------------------------------
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

    user_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE", nullable=True
    )
    user: "User" = Relationship(back_populates="folders")

    parent_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="folder.id", ondelete="CASCADE"
    )
    parent: Optional["Folder"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Folder.id"}
    )

    children: List["Folder"] = Relationship(back_populates="parent")
