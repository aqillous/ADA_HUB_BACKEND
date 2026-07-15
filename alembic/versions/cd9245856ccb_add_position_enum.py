"""add position enum

Revision ID: cd9245856ccb
Revises: 85e3bb82f81d
Create Date: 2026-07-15 22:03:23.116197

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd9245856ccb'
down_revision: Union[str, Sequence[str], None] = '85e3bb82f81d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


position_enum = sa.Enum(
    "igv_member",
    "igv_tl",
    "ogv_member",
    "ogv_tl",
    "lcvp",
    "lcp",
    "alumnus",
    name="positionenum",
)

def upgrade():
    position_enum.create(op.get_bind(), checkfirst=True)

    # Remove old values
    op.execute("UPDATE users SET current_position = NULL")

    op.alter_column(
        "users",
        "current_position",
        existing_type=sa.String(),
        type_=position_enum,
        existing_nullable=True,
        postgresql_using="current_position::positionenum",
    )


def downgrade():
    op.alter_column(
        "users",
        "current_position",
        existing_type=position_enum,
        type_=sa.String(),
        existing_nullable=True,
        postgresql_using="current_position::text",
    )

    position_enum.drop(op.get_bind(), checkfirst=True)
