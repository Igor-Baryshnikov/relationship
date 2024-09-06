"""add jwt to user

Revision ID: bc9e15f313d5
Revises: 3517b3a695d3
Create Date: 2024-09-04 23:43:40.857311

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc9e15f313d5'
down_revision: Union[str, None] = '3517b3a695d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('jwt_token', sa.Text(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'jwt_token')
    # ### end Alembic commands ###