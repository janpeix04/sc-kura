import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, DateTime, Relationship

from app.schemas.users import UserBase, UserKeyBase
from app.schemas.storage import FolderBase, FileBase
from app.schemas.crypto import EncryptedFileBase, EncryptedFolderBase

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
    keys: list["UserKey"] = Relationship(back_populates="user")
    encrypted_folders: list["EncryptedFolder"] = Relationship(back_populates="user")
    encrypted_files: list["EncryptedFile"] = Relationship(back_populates="user")


class UserKey(UserKeyBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    user_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )
    user: User | None = Relationship(back_populates="keys")


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
    original_parent_id: uuid.UUID | None = Field(default=None, foreign_key="folder.id")
    parent: Optional["Folder"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={
            "remote_side": "Folder.id",
            "foreign_keys": "[Folder.parent_id]",
        },
    )
    children: list["Folder"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"foreign_keys": "[Folder.parent_id]"},
    )

    files: list["File"] = Relationship(
        back_populates="folder",
        sa_relationship_kwargs={"foreign_keys": "[File.parent_id]"},
    )


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

    parent_id: uuid.UUID | None = Field(
        default=None, foreign_key="folder.id", ondelete="CASCADE"
    )
    original_parent_id: uuid.UUID | None = Field(default=None, foreign_key="folder.id")
    folder: Folder | None = Relationship(
        back_populates="files",
        sa_relationship_kwargs={"foreign_keys": "[File.parent_id]"},
    )


# -----------------------------------------------------------
#                  ENCRYPTED FOLDER MODEL
# -----------------------------------------------------------


class EncryptedFolder(EncryptedFolderBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )
    user: User | None = Relationship(back_populates="encrypted_folders")

    parent_id: uuid.UUID | None = Field(
        default=None, foreign_key="encryptedfolder.id", ondelete="CASCADE"
    )
    original_parent_id: uuid.UUID | None = Field(
        default=None, foreign_key="encryptedfolder.id"
    )
    parent: Optional["EncryptedFolder"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={
            "remote_side": "EncryptedFolder.id",
            "foreign_keys": "[EncryptedFolder.parent_id]",
        },
    )
    children: list["EncryptedFolder"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"foreign_keys": "[EncryptedFolder.parent_id]"},
    )

    files: list["EncryptedFile"] = Relationship(
        back_populates="folder",
        sa_relationship_kwargs={"foreign_keys": "[EncryptedFile.parent_id]"},
    )


# -----------------------------------------------------------
#                    ENCRYPTED FILE MODEL
# -----------------------------------------------------------


class EncryptedFile(EncryptedFileBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="CASCADE"
    )
    user: User | None = Relationship(back_populates="encrypted_files")

    parent_id: uuid.UUID | None = Field(
        default=None, foreign_key="encryptedfolder.id", ondelete="CASCADE"
    )
    original_parent_id: uuid.UUID | None = Field(
        default=None, foreign_key="encryptedfolder.id"
    )

    folder: EncryptedFolder | None = Relationship(
        back_populates="files",
        sa_relationship_kwargs={"foreign_keys": "[EncryptedFile.parent_id]"},
    )
