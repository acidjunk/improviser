"""empty message

Revision ID: e7431e9f9d5d
Revises: d015827d02ac
Create Date: 2019-03-19 21:24:48.280197

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e7431e9f9d5d"
down_revision = "d015827d02ac"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("riff_exercises", sa.Column("instrument_key", sa.String(length=3), nullable=True))
    op.add_column("riff_exercises", sa.Column("is_copyable", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("riff_exercises", "is_copyable")
    op.drop_column("riff_exercises", "instrument_key")
    # ### end Alembic commands ###
