"""Parent id folder ondelete cascade and fix enum casting

Revision ID: 40d7c68f831c
Revises: 5d0217eef010
Create Date: 2026-02-27 17:26:21.567811
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "40d7c68f831c"
down_revision: Union[str, Sequence[str], None] = "5d0217eef010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1️⃣ Create the new enum type
    op.execute(
        "CREATE TYPE filefolderstatus AS ENUM ('PENDING', 'UPLOADED', 'FAILED', 'DELETED');"
    )

    # 2️⃣ Convert 'file.status' from enum -> text -> new enum
    op.alter_column(
        "file",
        "status",
        type_=sa.Text(),
        existing_type=postgresql.ENUM(
            "PENDING", "UPLOADED", "FAILED", "DELETED", name="filestatus"
        ),
        postgresql_using="status::text",
        existing_nullable=False,
    )
    op.alter_column(
        "file",
        "status",
        type_=sa.Enum(
            "PENDING", "UPLOADED", "FAILED", "DELETED", name="filefolderstatus"
        ),
        postgresql_using="status::filefolderstatus",
        existing_nullable=False,
    )

    # 3️⃣ Same for 'folder.status'
    op.alter_column(
        "folder",
        "status",
        type_=sa.Text(),
        existing_type=postgresql.ENUM(
            "PENDING", "UPLOADED", "FAILED", "DELETED", name="filestatus"
        ),
        postgresql_using="status::text",
        existing_nullable=False,
    )
    op.alter_column(
        "folder",
        "status",
        type_=sa.Enum(
            "PENDING", "UPLOADED", "FAILED", "DELETED", name="filefolderstatus"
        ),
        postgresql_using="status::filefolderstatus",
        existing_nullable=False,
    )

    # 4️⃣ Update foreign key on folder.parent_id to CASCADE
    op.drop_constraint(op.f("folder_parent_id_fkey"), "folder", type_="foreignkey")
    op.create_foreign_key(
        None, "folder", "folder", ["parent_id"], ["id"], ondelete="CASCADE"
    )


def downgrade() -> None:
    # 1️⃣ Revert foreign key
    op.drop_constraint(None, "folder", type_="foreignkey")
    op.create_foreign_key(
        op.f("folder_parent_id_fkey"), "folder", "folder", ["parent_id"], ["id"]
    )

    # 2️⃣ Convert 'folder.status' back: enum -> text -> old enum
    op.alter_column(
        "folder",
        "status",
        type_=sa.Text(),
        existing_type=sa.Enum(
            "PENDING", "UPLOADED", "FAILED", "DELETED", name="filefolderstatus"
        ),
        postgresql_using="status::text",
        existing_nullable=False,
    )
    op.alter_column(
        "folder",
        "status",
        type_=postgresql.ENUM(
            "PENDING", "UPLOADED", "FAILED", "DELETED", name="filestatus"
        ),
        postgresql_using="status::filestatus",
        existing_nullable=False,
    )

    # 3️⃣ Same for 'file.status'
    op.alter_column(
        "file",
        "status",
        type_=sa.Text(),
        existing_type=sa.Enum(
            "PENDING", "UPLOADED", "FAILED", "DELETED", name="filefolderstatus"
        ),
        postgresql_using="status::text",
        existing_nullable=False,
    )
    op.alter_column(
        "file",
        "status",
        type_=postgresql.ENUM(
            "PENDING", "UPLOADED", "FAILED", "DELETED", name="filestatus"
        ),
        postgresql_using="status::filestatus",
        existing_nullable=False,
    )

    # 4️⃣ Drop the new enum type
    op.execute("DROP TYPE filefolderstatus;")
