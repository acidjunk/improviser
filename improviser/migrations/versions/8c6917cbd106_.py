"""empty message

Revision ID: 8c6917cbd106
Revises: ce5eaa98b9de
Create Date: 2018-10-06 21:00:28.280328

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c6917cbd106'
down_revision = 'ce5eaa98b9de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('riff_exercise_items', sa.Column('riff_root_key', sa.String(length=3), nullable=True))
    op.create_index(op.f('ix_riff_exercise_items_order_number'), 'riff_exercise_items', ['order_number'], unique=False)
    op.add_column('riffs', sa.Column('image_info', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('riffs', 'image_info')
    op.drop_index(op.f('ix_riff_exercise_items_order_number'), table_name='riff_exercise_items')
    op.drop_column('riff_exercise_items', 'riff_root_key')
    # ### end Alembic commands ###