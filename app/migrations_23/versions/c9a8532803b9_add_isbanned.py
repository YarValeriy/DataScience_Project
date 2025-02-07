"""

Revision ID: c9a8532803b9
Revises: d5b76df8c912
Create Date: 2024-05-24 20:53:20.056676

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9a8532803b9'
down_revision: Union[str, None] = 'd5b76df8c912'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'isLoggedIn')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('isLoggedIn', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
