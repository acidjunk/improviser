"""empty message

Revision ID: d514c6280b8a
Revises: bb7173894adb
Create Date: 2019-01-11 11:40:06.466389

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd514c6280b8a'
down_revision = 'bb7173894adb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('quick_token', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('quick_token_created_at', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_user_quick_token'), 'user', ['quick_token'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_quick_token'), table_name='user')
    op.drop_column('user', 'quick_token_created_at')
    op.drop_column('user', 'quick_token')
    # ### end Alembic commands ###