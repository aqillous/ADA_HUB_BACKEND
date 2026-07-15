"""enum update

Revision ID: a443254a4f56
Revises: b209a2cb9613
Create Date: 2026-07-15 23:14:22.916374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a443254a4f56'
down_revision: Union[str, Sequence[str], None] = 'b209a2cb9613'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "current_position",
        existing_type=sa.Enum(
            "igv_member", "igv_tl", "ogv_member", "ogv_tl", "lcvp", "lcp", "alumnus",
            name="positionenum",
        ),
        type_=sa.String(),
        existing_nullable=True,
        postgresql_using="current_position::text",
    )
    # Drop the now-unused native enum type (Postgres only)
    op.execute("DROP TYPE IF EXISTS positionenum")


def downgrade() -> None:
    positionenum = sa.Enum(
        "igv_member", "igv_tl", "ogv_member", "ogv_tl", "lcvp", "lcp", "alumnus",
        name="positionenum",
    )
    positionenum.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        "users",
        "current_position",
        existing_type=sa.String(),
        type_=positionenum,
        existing_nullable=True,
        postgresql_using="current_position::positionenum",
    )
