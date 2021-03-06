"""empty message

Revision ID: 5b825020b4db
Revises: e8fb166b4e11
Create Date: 2020-01-10 15:16:58.069786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5b825020b4db"
down_revision = "e8fb166b4e11"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("backing_tracks", sa.Column("approved", sa.Boolean(), nullable=True))
    op.add_column("backing_tracks", sa.Column("approved_at", sa.DateTime(), nullable=True))
    op.add_column("backing_tracks", sa.Column("modified_at", sa.DateTime(), nullable=True))
    op.drop_column("backing_tracks", "complete")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("backing_tracks", sa.Column("complete", sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column("backing_tracks", "modified_at")
    op.drop_column("backing_tracks", "approved_at")
    op.drop_column("backing_tracks", "approved")
    # ### end Alembic commands ###
