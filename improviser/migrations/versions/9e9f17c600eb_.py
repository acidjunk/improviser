"""empty message

Revision ID: 9e9f17c600eb
Revises: 60b80747bce6
Create Date: 2021-01-16 00:32:58.766762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e9f17c600eb'
down_revision = '60b80747bce6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('backing_tracks', sa.Column('number_of_bars', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('backing_tracks', 'number_of_bars')
    # ### end Alembic commands ###
