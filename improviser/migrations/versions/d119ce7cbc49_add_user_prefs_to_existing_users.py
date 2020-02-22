"""empty message

Revision ID: d119ce7cbc49
Revises: de9503a121ab
Create Date: 2019-01-15 17:01:21.954897

"""
import uuid
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d119ce7cbc49"
down_revision = "de9503a121ab"
branch_labels = None
depends_on = None


def get_users(conn):
    res = conn.execute(sa.text('SELECT id FROM "user"'))
    return res.fetchall()


def get_default_instrument(conn):
    res = conn.execute(sa.text("SELECT id FROM instruments WHERE name= 'Generic C'"))
    return res.fetchone()


def check_user_pref_needed(conn, user_id):
    res = conn.execute(sa.text(f"SELECT id from user_preferences WHERE user_id = '{user_id}'"))
    if res.fetchall():
        return False
    return True


def add_user_prefs_to_all_users(conn):
    instrument = get_default_instrument(conn)

    for user in get_users(conn):
        if check_user_pref_needed(conn, user[0]):
            conn.execute(
                sa.text(
                    """INSERT INTO user_preferences (id, instrument_id, user_id) VALUES 
                    (:id, :instrument_id, :user_id);"""
                ),
                id=uuid.uuid4(),
                user_id=user[0],
                instrument_id=instrument[0],
            )
            print(f"Created preference for user_id: {user[0]}")

        else:
            print(f"Skipping preference create for user_id: {user[0]}")


def upgrade():
    conn = op.get_bind()
    add_user_prefs_to_all_users(conn)


def downgrade():
    pass
