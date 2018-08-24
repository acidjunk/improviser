# coding:utf-8
import datetime
import uuid

from improviser.database import db


def convertToMusicXML(lilypond):
    import ly.musicxml
    e = ly.musicxml.writer()

    prefix = """\transpose c c {
    {
    \version "2.12.3"
    \clef treble
    \time 4/4
    \override Staff.TimeSignature #'stencil = ##f
    """
    postfix = """}
    }
    \paper{
                indent=0\mm
                line-width=120\mm
                oddFooterMarkup=##f
                oddHeaderMarkup=##f
                bookTitleMarkup = ##f
                scoreTitleMarkup = ##f
            }"""

    xml_header = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">"""  # noqa

    lilypond = f"{prefix}\n{lilypond}\n{postfix}"

    e.parse_text(lilypond)
    xml = bytes(xml_header, encoding='UTF-8') + e.musicxml().tostring()
    return {xml}


class Riff(db.Model):
    __tablename__ = 'riffs'
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = db.Column(db.String(255), unique=True, index=True)
    number_of_bars = db.Column(db.Integer())
    notes = db.Column(db.String(255))
    chord = db.Column(db.String(255), index=True)
    render_valid = db.Column(db.Boolean, default=False)
    render_date = db.Column(db.DateTime)
    riff_exercises = db.relationship('RiffExercise', secondary='riff_exercise_items',
                                     backref=db.backref('riffs', lazy='dynamic'))
    def __repr__(self):
        return '<Riff %r>' % self.name

class RiffExercise(db.Model):
    __tablename__ = 'riff_exercises'
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = db.Column(db.String(255))
    is_global = db.Column(db.Boolean, default=True)
    created_by = db.Column('created_by', db.UUID(as_uuid=True), db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<RiffExercise %r>' % self.name


class RiffExerciseItem(db.Model):
    __tablename__ = 'riff_exercise_items'
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    riff_exercise_id = db.Column('riff_exercise_id', db.UUID(as_uuid=True), db.ForeignKey('riff_exercises.id'))
    riff_id = db.Column('riff_id', db.UUID(as_uuid=True), db.ForeignKey('riffs.id'))
    riff_root_key = db.Column(db.String(3), default='c')
    order_number = db.Column(db.Integer, primary_key=True, index=True)
    created_by = db.Column('created_by', db.UUID(as_uuid=True), db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
