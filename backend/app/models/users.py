import uuid
from typing import List, TYPE_CHECKING
from datetime import datetime, timezone

from sqlmodel import Field, DateTime, Relationship
from app.schemas.users import UserBase

if TYPE_CHECKING:
    from app.models.storage import File, Folder, StorageMetadataField


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
    metadataFields: List["StorageMetadataField"] = Relationship(back_populates="user")
