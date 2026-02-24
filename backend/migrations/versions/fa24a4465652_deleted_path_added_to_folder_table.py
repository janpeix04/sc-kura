"""Deleted path added to Folder table

Revision ID: fa24a4465652
Revises: 5d0217eef010
Create Date: 2026-02-24 17:34:25.757041

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "fa24a4465652"
down_revision: Union[str, Sequence[str], None] = "5d0217eef010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create the new enum type
    op.execute(
        "CREATE TYPE filefolderstatus AS ENUM ('PENDING', 'UPLOADED', 'FAILED', 'DELETED');"
    )

    # 2. Alter 'file.status' to the new type, casting via text
    op.execute("""
        ALTER TABLE file
        ALTER COLUMN status TYPE filefolderstatus
        USING status::text::filefolderstatus;
    """)

    # 3. Add 'deleted_path' column to folder
    op.add_column("folder", sa.Column("deleted_path", sa.String(), nullable=True))

    # 4. Alter 'folder.status' to the new type, casting via text
    op.execute("""
        ALTER TABLE folder
        ALTER COLUMN status TYPE filefolderstatus
        USING status::text::filefolderstatus;
    """)


def downgrade() -> None:
    # 1. Alter 'folder.status' back to old enum
    op.execute("""
        ALTER TABLE folder
        ALTER COLUMN status TYPE filestatus
        USING status::text::filestatus;
    """)

    # 2. Drop 'deleted_path' column
    op.drop_column("folder", "deleted_path")

    # 3. Alter 'file.status' back to old enum
    op.execute("""
        ALTER TABLE file
        ALTER COLUMN status TYPE filestatus
        USING status::text::filestatus;
    """)

    # 4. Drop the new enum type
    op.execute("DROP TYPE filefolderstatus;")
