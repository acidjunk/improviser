import pytest
from database import User


def test_a_transaction(db_session):
   users = db_session.query(User).all()

