"""Create phone number for user column

Revision ID: f429faa3c032
Revises: 
Create Date: 2024-12-04 06:16:58.463800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f429faa3c032'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_number", sa.String(), nullable=True)) #type: ignore


def downgrade() -> None:
    op.drop_column("users", "phone_number")
