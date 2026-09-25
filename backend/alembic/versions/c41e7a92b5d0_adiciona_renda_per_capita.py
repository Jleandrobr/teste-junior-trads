"""adiciona renda domiciliar per capita

Revision ID: c41e7a92b5d0
Revises: 9876135566d9
Create Date: 2026-09-24 20:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c41e7a92b5d0'
down_revision: Union[str, None] = '9876135566d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('renda', sa.Column('rendimento_per_capita_medio', sa.Numeric(10, 2), nullable=False, server_default='0'))
    op.add_column('renda', sa.Column('rendimento_per_capita_mediano', sa.Numeric(10, 2), nullable=False, server_default='0'))
    op.alter_column('renda', 'rendimento_per_capita_medio', server_default=None)
    op.alter_column('renda', 'rendimento_per_capita_mediano', server_default=None)


def downgrade() -> None:
    op.drop_column('renda', 'rendimento_per_capita_mediano')
    op.drop_column('renda', 'rendimento_per_capita_medio')
