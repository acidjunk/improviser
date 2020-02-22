"""empty message

Revision ID: 9dd401b4375a
Revises: 7418f933e467
Create Date: 2019-04-12 23:23:09.204503

"""
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9dd401b4375a"
down_revision = "7418f933e467"
branch_labels = None
depends_on = None


def get_default_instrument(conn):
    res = conn.execute(sa.text("SELECT id FROM instruments WHERE name= 'Tenor saxophone'"))
    return res.fetchone()


def get_exercises(conn):
    res = conn.execute(sa.text("SELECT id FROM riff_exercises"))
    return res.fetchall()


def add_instrument_to_all_exercises(conn):
    instrument = get_default_instrument(conn)

    for exercise in get_exercises(conn):
        conn.execute(
            sa.text(
                """INSERT INTO riff_exercise_instruments(id, riff_exercise_id, instrument_id) VALUES 
                    (:id, :riff_exercise_id, :instrument_id);"""
            ),
            id=uuid.uuid4(),
            riff_exercise_id=exercise[0],
            instrument_id=instrument[0],
        )
        print(f"Populating instrument for exercise_id: {exercise[0]}")


def upgrade():
    conn = op.get_bind()
    add_instrument_to_all_exercises(conn)
    conn.execute(sa.text("""UPDATE riff_exercises SET stars=:stars"""), stars=3)


def downgrade():
    pass
