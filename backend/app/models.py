import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, DateTime, Relationship

from app.schemas.users import UserBase
from app.schemas.storage import FolderBase, FileBase

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

    folders: list["Folder"] = Relationship(back_populates="user")
    files: list["File"] = Relationship(back_populates="user")


# -----------------------------------------------------------
#                           FOLDER MODEL
# -----------------------------------------------------------


class Folder(FolderBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    modified_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    opened_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )
    user: User | None = Relationship(back_populates="folders")

    parent_id: uuid.UUID | None = Field(
        default=None, foreign_key="folder.id", ondelete="CASCADE"
    )
    parent: Optional["Folder"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Folder.id"}
    )
    children: list["Folder"] = Relationship(back_populates="parent")

    files: list["File"] = Relationship(back_populates="folder")


# -----------------------------------------------------------
#                           FILE MODEL
# -----------------------------------------------------------


class File(FileBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    modified_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    opened_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )
    user: User | None = Relationship(back_populates="files")

    folder_id: uuid.UUID | None = Field(
        default=None, foreign_key="folder.id", ondelete="CASCADE"
    )
    folder: Folder | None = Relationship(back_populates="files")
