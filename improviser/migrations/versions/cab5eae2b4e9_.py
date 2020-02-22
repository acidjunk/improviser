"""empty message

Revision ID: cab5eae2b4e9
Revises: 578b94c63af4
Create Date: 2019-02-19 15:17:49.021475

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cab5eae2b4e9"
down_revision = "578b94c63af4"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("riff_exercises", sa.Column("annotations", sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("riff_exercises", "annotations")
    # ### end Alembic commands ###
