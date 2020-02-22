"""number_of_bars

Revision ID: 0afe6098309b
Revises: b96c1a140fa3
Create Date: 2019-02-19 16:17:03.239179

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from migrations.helpers import get_riff_by_id

revision = "0afe6098309b"
down_revision = "b96c1a140fa3"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    exercise_items = conn.execute(sa.text("SELECT * FROM riff_exercise_items")).fetchall()
    for item in exercise_items:
        riff = get_riff_by_id(conn, item[2])
        conn.execute(
            sa.text("""UPDATE riff_exercise_items SET number_of_bars=:number_of_bars WHERE id=:id"""),
            number_of_bars=int(riff[2]),
            id=str(item[0]),
        )


def downgrade():
    pass
