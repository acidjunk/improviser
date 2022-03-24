"""empty message

Revision ID: 5a5a1576f2de
Revises: a35761a62430
Create Date: 2022-01-12 02:04:41.374516

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a5a1576f2de'
down_revision = 'a35761a62430'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('backing_tracks', 'is_scale')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('backing_tracks', sa.Column('is_scale', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###