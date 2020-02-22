"""empty message

Revision ID: b618481ac94e
Revises: f16ffded1edc
Create Date: 2019-03-21 22:57:23.715860

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b618481ac94e"
down_revision = "f16ffded1edc"
branch_labels = None
depends_on = None


def set_instrument_pitch(conn):
    conn.execute(sa.text(f"UPDATE riff_exercises SET created_by='4af1f7f5-4781-4607-bf6c-f0388f7f4527'"))


def upgrade():
    conn = op.get_bind()
    set_instrument_pitch(conn)


def downgrade():
    pass
