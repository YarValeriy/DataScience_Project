"""drop blacklist_tokens table and related constraints

Revision ID: <your_revision_id>
Revises: <previous_revision_id>
Create Date: <date>

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '23ab9ae7629f'
down_revision: Union[str, None] = '2791e9525d52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.has_table(conn, 'blacklist_tokens'):
        # Drop any foreign key constraints if needed
        # e.g., op.drop_constraint('constraint_name', 'blacklist_tokens', type_='foreignkey')
        
        op.drop_table('blacklist_tokens')

def downgrade() -> None:
    # Add code here to re-create the table if needed for downgrade
    pass
