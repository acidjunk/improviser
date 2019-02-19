import sqlalchemy as sa
from more_itertools import one


def get_riff_by_id(conn, id):
    result = conn.execute(sa.text("SELECT * FROM riffs WHERE id=:id"), id=id)
    return one(result.fetchall())
