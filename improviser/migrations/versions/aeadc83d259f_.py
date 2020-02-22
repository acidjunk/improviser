"""empty message

Revision ID: aeadc83d259f
Revises: 1c040127f674
Create Date: 2019-01-25 23:58:53.034718

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "aeadc83d259f"
down_revision = "1c040127f674"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("riff_exercises", sa.Column("description", sa.String(), nullable=True))
    op.add_column("riff_exercises", sa.Column("root_key", sa.String(length=3), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("riff_exercises", "root_key")
    op.drop_column("riff_exercises", "description")
    # ### end Alembic commands ###
