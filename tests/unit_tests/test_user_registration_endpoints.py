import pytest
from database import User


def test_something(db_session):
   users = db_session.query(User).all()
