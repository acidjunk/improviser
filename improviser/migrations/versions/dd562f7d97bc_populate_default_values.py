"""Populate default values

Revision ID: dd562f7d97bc
Revises: 2e8d1f0237ea
Create Date: 2018-11-20 15:36:10.478864

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd562f7d97bc'
down_revision = '2e8d1f0237ea'
branch_labels = None
depends_on = None

def set_creation_date(c):
    c.execute(sa.text(f"UPDATE riffs SET created_date='2018-03-01 00:00:00', multi_chord=FALSE WHERE created_date IS NULL"))
    c.execute(sa.text(f"UPDATE riffs SET scale_trainer_enabled=TRUE WHERE number_of_bars=1 OR number_of_bars=2"))


def upgrade():
    conn = op.get_bind()
    set_creation_date(conn)


def downgrade():
    pass
