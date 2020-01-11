import hashlib
import sqlalchemy

import datetime
import uuid

from flask_security import RoleMixin, UserMixin, SQLAlchemySessionUserDatastore
from flask_sqlalchemy import SQLAlchemy
from libgravatar import Gravatar

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
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean())
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary='roles_users', backref=backref('users', lazy='dynamic'))

    mail_offers = Column(Boolean, default=False)
    mail_announcements = Column(Boolean, default=True)

    quick_token = Column(String(255), index=True)
    quick_token_created_at = Column(DateTime())

    fs_uniquifier = Column(String(255))

    # Human-readable values for the User when editing user related stuff.
    def __str__(self):
        return f'{self.username} : {self.email}'

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.email)


class Instrument(db.Model):
    __tablename__ = 'instruments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), unique=True)
    root_key = Column(String(3), default='c')

    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    def __str__(self):
        return f'Instrument: {self.name}, Key: {self.root_key}'


class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    instrument_id = Column('instrument_id', UUID(as_uuid=True), ForeignKey('instruments.id'))
    instrument = relationship("Instrument", backref=backref("parent", uselist=False))
    user_id = Column('user_id', UUID(as_uuid=True), ForeignKey('user.id'))
    user = relationship("User", backref=backref("preferences", uselist=False))
    recent_exercises = Column(JSON)
    recent_lessons = Column(JSON)
    language = Column(String(2), default='en')
    ideabook = Column(JSON)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(60), unique=True, index=True)

    def __repr__(self):
        return self.name


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
    # Todo: rename to created_at (to reflect naming convention)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    image_info = Column(JSON)
    riff_tags = relationship("Tag", secondary='riff_tags')
    riff_to_tags = relationship("RiffTag")

    def __repr__(self):
        return '<Riff %r %s bars, id:%s>' % (self.name, self.number_of_bars, self.id)


class RiffExercise(db.Model):
    __tablename__ = 'riff_exercises'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255))
    description = Column(String())
    root_key = Column(String(3))
    instrument_key = Column(String(3), default="c")
    is_public = Column(Boolean, default=False)
    is_copyable = Column(Boolean, default=False)
    stars = Column(Integer, default=3)
    created_by = Column('created_by', UUID(as_uuid=True), ForeignKey('user.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.datetime.utcnow)
    annotations = Column(JSON)
    tempo = Column(Integer())
    user = relationship("User", backref=backref("riff_exercises", uselist=False))
    riff_exercise_tags = relationship("Tag", secondary="riff_exercise_tags")
    riff_exercise_to_tags = relationship("RiffExerciseTag")
    riff_exercise_items = relationship("RiffExerciseItem", cascade="all, delete-orphan", backref="parent")
    instruments = relationship("Instrument", secondary="riff_exercise_instruments")

    def __repr__(self):
        return '<RiffExercise %r %s>>' % (self.name, self.id)

    @property
    def gravatar_image(self):
        g = Gravatar(self.user.email)
        return g.get_image(size=100)


class RiffExerciseItem(db.Model):
    __tablename__ = 'riff_exercise_items'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    riff_exercise_id = Column('riff_exercise_id', UUID(as_uuid=True), ForeignKey('riff_exercises.id'))
    riff_id = Column('riff_id', UUID(as_uuid=True), ForeignKey('riffs.id'))
    number_of_bars = Column(Integer())
    text_info = Column(String(255))
    chord_info = Column(String(255))
    chord_info_alternate = Column(String(255))
    chord_info_backing_track = Column(String(255))
    pitch = Column(String(3), default='c')
    octave = Column(Integer(), default=0)
    order_number = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.datetime.utcnow)

    # not sure if we want this:
    riff = relationship("Riff")

    def __repr__(self):
        return f'<RiffItem {self.riff.name} in {self.pitch}/{self.octave} chords: {self.chord_info}'


# Setup tagging for all resources that need it
class RiffTag(db.Model):
    __tablename__ = 'riff_tags'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    riff_id = Column('riff_id', UUID(as_uuid=True), ForeignKey('riffs.id'), index=True)
    tag_id = Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.id'), index=True)
    riff = db.relationship("Riff", lazy=True)
    tag = db.relationship("Tag", lazy=True)

    def __repr__(self):
        return self.tag.name


class RiffExerciseTag(db.Model):
    __tablename__ = 'riff_exercise_tags'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    riff_exercise_id = Column('riff_exercise_id', UUID(as_uuid=True), ForeignKey('riff_exercises.id'), index=True)
    tag_id = Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.id'), index=True)
    riff_exercise = db.relationship("RiffExercise", lazy=True)
    tag = db.relationship("Tag", lazy=True)

    def __repr__(self):
        return self.tag.name


class RiffExerciseInstrument(db.Model):
    __tablename__ = 'riff_exercise_instruments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    riff_exercise_id = Column('riff_exercise_id', UUID(as_uuid=True), ForeignKey('riff_exercises.id'), index=True)
    instrument_id = Column('instrument_id', UUID(as_uuid=True), ForeignKey('instruments.id'), index=True)


class BackingTrack(db.Model):
    __tablename__ = 'backing_tracks'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    tempo = Column(Integer, default=100)
    chord_info = Column(String, nullable=False)
    file = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.datetime.utcnow)
    approved_at = Column(DateTime)
    approved = Column("approved", Boolean(), default=False)


user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
