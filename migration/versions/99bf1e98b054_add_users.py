"""add users

Revision ID: 99bf1e98b054
Revises: bdfaa255d3b3
Create Date: 2025-03-22 19:33:24.926373

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99bf1e98b054'
down_revision: Union[str, None] = 'bdfaa255d3b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('registered_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.alter_column('links', 'login_user',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('links', 'full_link',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('links', 'short_link',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('links', 'is_deleted',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('links', 'is_deleted',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('links', 'short_link',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('links', 'full_link',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('links', 'login_user',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###
