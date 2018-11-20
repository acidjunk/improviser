import datetime
import uuid

from flask_security import RoleMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

db = SQLAlchemy()


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', UUID(as_uuid=True), ForeignKey('user.id'))
    role_id = Column('role_id', UUID(as_uuid=True), ForeignKey('role.id'))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary='roles_users', backref=backref('users', lazy='dynamic'))

    # Human-readable values for the User when editing user related stuff.
    def __str__(self):
        return f'{self.username} : {self.email}'

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.email)


class Riff(db.Model):
    __tablename__ = 'riffs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), unique=True, index=True)
    number_of_bars = Column(Integer())
    notes = Column(String(255))
    chord = Column(String(255), index=True)
    chord_info = Column(String(255))
    multi_chord = Column(Boolean, default=False)
    scale_trainer_enabled = Column(Boolean, default=False)
    render_valid = Column(Boolean, default=False)
    render_date = Column(DateTime)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    image_info = Column(JSON)
    riff_exercises = relationship('RiffExercise', secondary='riff_exercise_items',
                                  backref=backref('riffs', lazy='dynamic'))
    def __repr__(self):
        return '<Riff %r>' % self.name


class RiffExercise(db.Model):
    __tablename__ = 'riff_exercises'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255))
    is_global = Column(Boolean, default=True)
    created_by = Column('created_by', UUID(as_uuid=True), ForeignKey('user.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<RiffExercise %r>' % self.name


class RiffExerciseItem(db.Model):
    __tablename__ = 'riff_exercise_items'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    riff_exercise_id = Column('riff_exercise_id', UUID(as_uuid=True), ForeignKey('riff_exercises.id'))
    riff_id = Column('riff_id', UUID(as_uuid=True), ForeignKey('riffs.id'))
    riff_root_key = Column(String(3), default='c')
    order_number = Column(Integer, primary_key=True, index=True)
    created_by = Column('created_by', UUID(as_uuid=True), ForeignKey('user.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
