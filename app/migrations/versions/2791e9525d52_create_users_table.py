"""create users table

Revision ID: 2791e9525d52
Revises: c9a8532803b9
Create Date: 2024-09-05 22:16:04.259400

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2791e9525d52'
down_revision: Union[str, None] = 'c9a8532803b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the ENUM type
role_enum = postgresql.ENUM('admin', 'moderator', 'user', name='role', create_type=False)

def upgrade() -> None:
    # Check if the ENUM type already exists
    conn = op.get_bind()
    if not conn.dialect.has_type(conn, 'role'):
        role_enum.create(conn)

    op.create_table('blacklist_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=500), nullable=False),
    sa.Column('blacklisted_on', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=True),
    sa.Column('email', sa.String(length=250), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=13), nullable=True),
    sa.Column('birthday', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('avatar', sa.String(length=255), nullable=True),
    sa.Column('refresh_token', sa.String(length=255), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('role', role_enum, nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone')
    )

def downgrade() -> None:
    # Drop the ENUM type first
    conn = op.get_bind()
    if conn.dialect.has_type(conn, 'role'):
        role_enum.drop(conn)
        
    op.drop_table('users')
    op.drop_table('blacklist_tokens')