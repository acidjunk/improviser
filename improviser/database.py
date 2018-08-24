from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql.base import UUID


db = SQLAlchemy()
db.UUID = UUID


def drop_all():
    db.drop_all()


def create_all():
    db.create_all()


def remove_session():
    db.session.remove()
