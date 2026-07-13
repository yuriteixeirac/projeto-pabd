"""add descricao and tipo to quarto

Revision ID: 6f7a3e9b1c2d
Revises: 8cae8164cad5
Create Date: 2026-07-12 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6f7a3e9b1c2d"
down_revision: Union[str, Sequence[str], None] = "8cae8164cad5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("quarto", sa.Column("descricao", sa.Text(), nullable=False, server_default=""))
    op.add_column(
        "quarto",
        sa.Column("tipo", sa.String(16), nullable=False, server_default="casal"),
    )
    op.alter_column("quarto", "descricao", server_default=None)
    op.alter_column("quarto", "tipo", server_default=None)


def downgrade() -> None:
    op.drop_column("quarto", "tipo")
    op.drop_column("quarto", "descricao")
