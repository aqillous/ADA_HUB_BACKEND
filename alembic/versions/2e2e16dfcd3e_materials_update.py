"""materials update

Revision ID: 2e2e16dfcd3e
Revises: e20aa08cacce
Create Date: 2026-07-19 00:23:35.036386

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e2e16dfcd3e'
down_revision: Union[str, Sequence[str], None] = 'e20aa08cacce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('material_folders', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.add_column('material_folders', sa.Column('allowed_emails', sa.String(), nullable=False, server_default=''))
    op.add_column('material_folders', sa.Column('color', sa.String(), nullable=False, server_default='blue'))
    op.add_column('material_folders', sa.Column('icon', sa.String(), nullable=False, server_default='folder'))
    op.create_foreign_key(None, 'material_folders', 'material_folders', ['parent_id'], ['id'])

    # optional: drop the server defaults now that existing rows are backfilled,
    # so the column relies on the ORM-level default() going forward instead
    op.alter_column('material_folders', 'allowed_emails', server_default=None)
    op.alter_column('material_folders', 'color', server_default=None)
    op.alter_column('material_folders', 'icon', server_default=None)


def downgrade() -> None:
    op.drop_constraint(None, 'material_folders', type_='foreignkey')
    op.drop_column('material_folders', 'icon')
    op.drop_column('material_folders', 'color')
    op.drop_column('material_folders', 'allowed_emails')
    op.drop_column('material_folders', 'parent_id')
