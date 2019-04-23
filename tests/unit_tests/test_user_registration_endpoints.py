import uuid

import pytest
from database import User, Riff, db


def test_something(db_session):
    assert True
    riff = Riff(
        id=str(uuid.uuid4()),
        name="Test riff 1",
        number_of_bars=1,
        notes=""
    )
    # db.add(riff)
    db_session.add(riff)
    db_session.commit()

    # test with query
    riff_db = Riff.query.first()
    print(riff_db)
    assert riff_db


def test_something_2():
    assert True
    riff = Riff(
        id=str(uuid.uuid4()),
        name="Test riff 2",
        number_of_bars=1,
        notes=""
    )
    # db.add(riff)
    db.session.add(riff)
    db.session.commit()

    # test with query
    riff_db = Riff.query.first()
    print(riff_db)
    assert riff_db


def test_something_3():
    assert True
    riff = Riff(
        id=str(uuid.uuid4()),
        name="Test riff 3",
        number_of_bars=1,
        notes=""
    )
    # db.add(riff)
    db.session.add(riff)
    db.session.commit()

    # test with query
    riff_db = Riff.query.first()
    print(riff_db)
    assert riff_db
