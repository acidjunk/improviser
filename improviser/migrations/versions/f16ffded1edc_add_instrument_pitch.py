"""empty message

Revision ID: f16ffded1edc
Revises: e7431e9f9d5d
Create Date: 2019-03-19 21:52:14.184671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f16ffded1edc"
down_revision = "e7431e9f9d5d"
branch_labels = None
depends_on = None


def set_instrument_pitch(conn):
    conn.execute(sa.text(f"UPDATE riff_exercises SET instrument_key='bes', is_copyable=TRUE WHERE is_public=TRUE"))
    conn.execute(sa.text(f"UPDATE riff_exercises SET instrument_key='bes', is_copyable=FALSE WHERE is_public=FALSE"))
    conn.execute(sa.text(f"UPDATE riff_exercises SET root_key='c' WHERE root_key IS NULL"))


def upgrade():
    conn = op.get_bind()
    set_instrument_pitch(conn)


def downgrade():
    pass
