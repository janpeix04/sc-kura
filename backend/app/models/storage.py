import uuid
from typing import TYPE_CHECKING
from datetime import datetime, timezone

from sqlmodel import Field, DateTime, Relationship
from app.schemas.storage import FileBase

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
