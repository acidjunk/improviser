import enum
import hashlib
import sqlalchemy

import datetime
import uuid

from flask_security import RoleMixin, UserMixin, SQLAlchemySessionUserDatastore
from flask_sqlalchemy import SQLAlchemy
from libgravatar import Gravatar

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, Float, JSON, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

db = SQLAlchemy()


class RolesUsers(db.Model):
    __tablename__ = "roles_users"
    id = Column(Integer(), primary_key=True)
    user_id = Column("user_id", UUID(as_uuid=True), ForeignKey("user.id"))
    role_id = Column("role_id", UUID(as_uuid=True), ForeignKey("role.id"))


class Role(db.Model, RoleMixin):
    __tablename__ = "role"
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
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True)
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean())
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    confirmed_at = Column(DateTime())
    roles = relationship("Role", secondary="roles_users", backref=backref("users", lazy="dynamic"))

    mail_offers = Column(Boolean, default=False)
    mail_announcements = Column(Boolean, default=True)

    quick_token = Column(String(255), index=True)
    quick_token_created_at = Column(DateTime())

    fs_uniquifier = Column(String(255))

    # Human-readable values for the User when editing user related stuff.
    def __str__(self):
        return f"{self.username} : {self.email}"

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.email)


class Instrument(db.Model):
    __tablename__ = "instruments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), unique=True)
    root_key = Column(String(3), default="c")

    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    def __str__(self):
        return f"Instrument: {self.name}, Key: {self.root_key}"


class UserPreference(db.Model):
    __tablename__ = "user_preferences"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    instrument_id = Column("instrument_id", UUID(as_uuid=True), ForeignKey("instruments.id"))
    instrument = relationship("Instrument", backref=backref("parent", uselist=False))
    user_id = Column("user_id", UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship("User", backref=backref("preferences", uselist=False))
    language = Column(String(2), default="en")
    ideabook = Column(JSON)


class Tag(db.Model):
    __tablename__ = "tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(60), unique=True, index=True)

    riffs_to_tags = relationship("RiffTag", cascade="save-update, merge, delete")
    riff_exercises_to_tags = relationship("RiffExerciseTag", cascade="save-update, merge, delete")

    def __repr__(self):
        return self.name


class Riff(db.Model):
    __tablename__ = "riffs"
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
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column("created_by", UUID(as_uuid=True), ForeignKey("user.id"))
    image_info = Column(JSON)
    riff_tags = relationship("Tag", secondary="riff_tags")
    riff_to_tags = relationship("RiffTag")
    is_public = Column(Boolean, default=False)

    def __repr__(self):
        return "<Riff %r %s bars, id:%s>" % (self.name, self.number_of_bars, self.id)


class RiffExercise(db.Model):
    __tablename__ = "riff_exercises"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255))
    description = Column(String())
    root_key = Column(String(3))
    instrument_key = Column(String(3), default="c")
    is_public = Column(Boolean, default=False)
    is_copyable = Column(Boolean, default=False)
    stars = Column(Integer, default=3)
    created_by = Column("created_by", UUID(as_uuid=True), ForeignKey("user.id"))
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
        return "<RiffExercise %r %s>>" % (self.name, self.id)

    @property
    def get_normalised_chord_info(self):
        # chord_info: string of lilypond chord stuff / bar
        chord_info = []
        for item in self.riff_exercise_items:
            # First first check if chord_info is avail in item relation
            if item.chord_info:
                chord_info.append(item.chord_info)
        return chord_info

    @property
    def gravatar_image(self):
        g = Gravatar(self.user.email)
        return g.get_image(size=100)


class RiffExerciseItem(db.Model):
    __tablename__ = "riff_exercise_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    riff_exercise_id = Column("riff_exercise_id", UUID(as_uuid=True), ForeignKey("riff_exercises.id"))
    riff_id = Column("riff_id", UUID(as_uuid=True), ForeignKey("riffs.id"))
    number_of_bars = Column(Integer())
    text_info = Column(String(255))
    chord_info = Column(String(255))
    chord_info_alternate = Column(String(255))
    chord_info_backing_track = Column(String(255))
    pitch = Column(String(3), default="c")
    octave = Column(Integer(), default=0)
    order_number = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.datetime.utcnow)

    # not sure if we want this:
    riff = relationship("Riff")

    def __repr__(self):
        return f"<RiffItem {self.riff.name} in {self.pitch}/{self.octave} chords: {self.chord_info}"


class RecentRiffExercise(db.Model):
    __tablename__ = "recent_riff_exercises"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    modified_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column("created_by", UUID(as_uuid=True), ForeignKey("user.id"))
    riff_exercise_id = Column("riff_exercise_id", UUID(as_uuid=True), ForeignKey("riff_exercises.id"), index=True)
    riff_exercise = relationship("RiffExercise", backref=backref("recent_riff_exercises", uselist=False))

    @property
    def riff_exercise_name(self):
        return self.riff_exercise.name


# Setup tagging for all resources that need it
class RiffTag(db.Model):
    __tablename__ = "riff_tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    riff_id = Column("riff_id", UUID(as_uuid=True), ForeignKey("riffs.id"), index=True)
    tag_id = Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id"), index=True)
    riff = db.relationship("Riff", lazy=True)
    tag = db.relationship("Tag", lazy=True)

    def __repr__(self):
        return self.tag.name


class RiffExerciseTag(db.Model):
    __tablename__ = "riff_exercise_tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    riff_exercise_id = Column("riff_exercise_id", UUID(as_uuid=True), ForeignKey("riff_exercises.id"), index=True)
    tag_id = Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id"), index=True)
    riff_exercise = db.relationship("RiffExercise", lazy=True)
    tag = db.relationship("Tag", lazy=True)

    def __repr__(self):
        return self.tag.name


class RiffExerciseInstrument(db.Model):
    __tablename__ = "riff_exercise_instruments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    riff_exercise_id = Column("riff_exercise_id", UUID(as_uuid=True), ForeignKey("riff_exercises.id"), index=True)
    instrument_id = Column("instrument_id", UUID(as_uuid=True), ForeignKey("instruments.id"), index=True)


class BackingTrack(db.Model):
    __tablename__ = "backing_tracks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    count_in = Column(Float(), default=0) # amount of seconds before the music starts in the audio. E.g. 1.4 for 1.4s
    intro_number_of_bars = Column(Integer(), default=0)  # amount of bars before loop
    number_of_bars = Column(Integer())  # total amount of bars (with intro and coda)
    coda_number_of_bars = Column(Integer(), default=0)  # amount of bars after loop
    tempo = Column(Integer, default=100)
    chord_info = Column(String, nullable=True)
    file = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.datetime.utcnow)
    approved_at = Column(DateTime)
    approved = Column("approved", Boolean(), default=False)


class Lesson(db.Model):
    __tablename__ = "lessons"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255))
    blog_intro = Column(String())
    blog_publish = Column(Boolean, default=True)
    created_by = Column("created_by", UUID(as_uuid=True), ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", backref=backref("lessons", uselist=False))

    def __repr__(self):
        return "<Lesson %r %s>" % (self.name, self.id)


class LessonItemEnum(enum.Enum):
    TEXT = 1
    RIFF = 2
    RIFF_EXERCISE = 3
    BACKING_TRACK = 4
    YOUTUBE = 3


class LessonItem(db.Model):
    __tablename__ = "lesson_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    item_type = Column(Enum(LessonItemEnum))
    lesson_id = Column("lesson_id", UUID(as_uuid=True), ForeignKey("lessons.id"))
    riff_id = Column("riff_id", UUID(as_uuid=True), ForeignKey("riffs.id"), nullable=True)
    riff_pitch = Column(String(3), nullable=True)
    riff_octave = Column(Integer(), nullable=True)
    riff_chord_info = Column(String(20), nullable=True)
    riff_exercise_id = Column("riff_exercise_id", UUID(as_uuid=True), ForeignKey("riff_exercises.id"), nullable=True)
    backing_track_id = Column("backing_track_id", UUID(as_uuid=True), ForeignKey("backing_tracks.id"), nullable=True)
    item_label = Column(String(255), nullable=True)
    item_text = Column(String(), nullable=True)
    order_number = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<LessonItem {self.item_type} with ID {self.id}>"


user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
