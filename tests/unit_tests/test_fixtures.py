import uuid

from database import Riff, db


def test_riff(app, riff):
    # test with query
    riff = Riff.query.get(riff.id)
    assert riff.name == 'Major 9 chord up down'


def test_isolation(app):
    riff = Riff(
        id=str(uuid.uuid4()),
        name="Test riff 1",
        number_of_bars=1,
        notes=""
    )
    # db.add(riff)
    db.session.add(riff)
    db.session.commit()

    # test with query
    riff_db = Riff.query.first()
    assert riff_db


def test_isolation2(app):
    riff = Riff(
        id=str(uuid.uuid4()),
        name="Test riff 3",
        number_of_bars=1,
        notes=""
    )
    db.session.add(riff)
    db.session.commit()

    # test with query
    riff_db = Riff.query.first()
    assert riff_db


def test_user(app, student):
    assert student.preferences
    assert student.preferences.instrument.name == "Generic C"
