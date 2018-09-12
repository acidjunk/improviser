"""empty message

Revision ID: ce5eaa98b9de
Revises: 983b4e76d8cb
Create Date: 2018-08-18 01:39:19.070722

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ce5eaa98b9de'
down_revision = '983b4e76d8cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('riff_exercise_items', sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('riff_exercise_items', sa.Column('order_number', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'riff_exercise_items', 'user', ['created_by'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'riff_exercise_items', type_='foreignkey')
    op.drop_index(op.f('ix_riff_exercise_items_order_number'), table_name='riff_exercise_items')
    op.drop_column('riff_exercise_items', 'order_number')
    op.drop_column('riff_exercise_items', 'created_by')
    # ### end Alembic commands ###
