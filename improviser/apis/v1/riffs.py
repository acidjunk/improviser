import datetime
import json
from database import db
from flask import request
from flask_login import login_required, current_user
from flask_restplus import Namespace, Resource, fields, marshal_with, reqparse, abort
from database import Riff
from flask_security import roles_required, auth_token_required, roles_accepted

KEYS = ["c", "cis", "d", "dis", "ees", "e", "f", "fis", "g", "gis", "aes", "a", "ais", "bes", "b"]
OCTAVES = [-1, 0, 1, 2]

api = Namespace("riffs", description="Riff related operations")


riff_serializer = api.model("Riff", {
    "name": fields.String(required=True, description="Unique riff name"),
    "number_of_bars": fields.Integer(required=True, description="Number of bars"),
    "notes": fields.String(required=True, description="Lilypond representation of the riff"),
    "chord": fields.String(description="Chord if known"),
    "multi_chord": fields.Boolean(description="Multiple chords in this riff?"),
    "chord_info": fields.String(),
})

riff_render_serializer = api.model("RenderedRiff", {
    "render_valid": fields.Boolean(required=True, description="Whether a render is deemed valid."),
    "image_info": fields.String(description="The metainfo for all images for this riff, per key, octave")
})

riff_exercise_serializer = api.model("RiffExercise", {
    "name": fields.String(required=True, description="Unique exercise name"),
    "is_global": fields.Boolean(description="Is this riff exercise visible to everyone?", default=False),
})

# Todo: make this a nested list: so order can be dealt with easily
riff_exercise_item_serializer = api.model("RiffExerciseItem", {
    "riff_exercise_id": fields.String(required=True, description="Unique exercise name"),
    "riff_id": fields.Boolean(description="Is this riff exercise visible to everyone?"),
})

image_info_marshaller = {
    "key_octave": fields.String,
    "width": fields.Integer,
    "height": fields.Integer,
    "staff_center": fields.Integer,
}

riff_fields = {
    'id': fields.String,
    'difficulty': fields.String,
    'name': fields.String,
    'number_of_bars': fields.Integer,
    'chord_info': fields.String,
    'chord': fields.String,
    'multi_chord': fields.Boolean,
    'image': fields.String,
    'image_info': fields.Nested(image_info_marshaller),
    'render_valid': fields.Boolean,
    'render_date': fields.DateTime,
    'created_date': fields.DateTime,
    'tags': fields.List(fields.String),
}

music_xml_info_marshaller = {
    "key_octave": fields.String,
    "music_xml": fields.String,
}

riff_detail_fields = {
    **riff_fields,
    'notes': fields.String,
    'music_xml_info': fields.List(
        fields.Nested(music_xml_info_marshaller),
        description='Music XML representation of the riff in all available keys')
}

riff_exercise_fields = {
    'name': fields.String,
    # 'riffs': fields.List,
    'created_by': fields.String,  # or UUID of the user?
    'created_at': fields.DateTime,
}

riff_exercise_detail_fields = riff_exercise_fields
# Todo: investigate: e.g. use a deep_copy?
riff_exercise_detail_fields["riffs"] = fields.List(fields.Nested(riff_fields))

riff_arguments = reqparse.RequestParser()
riff_arguments.add_argument('search_phrase', type=str, required=False,
                            help='Return only items that contain the search_phrase')
riff_arguments.add_argument('show_unrendered', type=bool, required=False, default=False,
                            help='Toggle so you can see unrendered riffs also')

riff_exercise_arguments = reqparse.RequestParser()
riff_exercise_arguments.add_argument('search_phrase', type=str, required=False,
                                     help='Return only items that contain the search_phrase')


def convertToMusicXML(lilypond, tranpose='c'):
    import ly.musicxml
    e = ly.musicxml.writer()

    prefix = """\\transpose c %s {
    {
    \\version "2.12.3"
    \\clef treble
    \\time 4/4
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
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">"""

    lilypond = f"{prefix % tranpose}\n{lilypond}\n{postfix}"
    e.parse_text(lilypond)
    # xml = bytes(xml_header, encoding='UTF-8') + e.musicxml().tostring()
    # return {xml}
    xml = xml_header + str(e.musicxml().tostring())
    return xml


@api.route('/')
@api.doc("Show all riffs to users with sufficient rights. Provides the ability to filter on riff status and to search.")
class RiffResourceList(Resource):

    @auth_token_required
    @roles_accepted('admin', 'moderator', 'member', 'student', 'teacher')
    @marshal_with(riff_fields)
    @api.expect(riff_arguments)
    def get(self):
        args = request.args
        # handle case insensitive search
        if args.get("search_phrase"):
            riffs_query = Riff.query.filter(Riff.name.ilike('%' + args["search_phrase"] + '%'))
        else:
            riffs_query = Riff.query

        # show all riffs or only rendered?
        show = "rendered"
        if args.get("show_unrendered") and args["show_unrendered"] == "true":
            show = "all"
        if "all" not in show:
            riffs_query = riffs_query.filter(Riff.render_valid)

        riffs = riffs_query.all()
        for riff in riffs:
            riff.tags = [str(tag.name) for tag in riff.riff_tags]
            riff.image = f"https://www.improviser.education/static/rendered/120/riff_{riff.id}_c.png"
        return riffs

    @auth_token_required
    @roles_accepted('admin', 'moderator', 'teacher')
    @api.expect(riff_serializer)
    def post(self):
        riff = Riff(**api.payload)
        try:
            db.session.add(riff)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            abort(400, 'DB error: {}'.format(str(error)))
        return 201


@api.route('/<string:riff_id>')
class RiffResource(Resource):

    @auth_token_required
    @roles_accepted('admin', 'moderator', 'member', 'student', 'teacher')
    @marshal_with(riff_detail_fields)
    def get(self, riff_id):
        riff = Riff.query.filter(Riff.id == riff_id).first()
        riff.tags = [str(tag.name) for tag in riff.riff_tags]
        riff.image = f"https://www.improviser.education/static/rendered/120/riff_{riff.id}_c.png"
        # todo: marshall dict -> key:music_xml
        result = []
        for octave in OCTAVES:
            result += [{"key_octave": key if not octave else f"{key}_{octave}",
                        "music_xml": convertToMusicXML(riff.notes, key)} for key in KEYS]
        riff.music_xml_info = result
        return riff

    @auth_token_required
    @roles_accepted('admin', 'moderator', 'teacher')
    @api.expect(riff_serializer)
    def put(self, riff_id):
        riff = Riff.query.filter_by(id=riff_id).first()
        # Todo implement real update
        return 204


@api.route('/rendered/<string:riff_id>')
class RiffResourceRendered(Resource):

    @auth_token_required
    @roles_accepted('admin')
    @api.expect(riff_render_serializer)
    def put(self, riff_id):
        riff = Riff.query.filter_by(id=riff_id).first()
        riff.render_valid = api.payload["render_valid"]
        riff.image_info = api.payload["image_info"]
        riff.render_date = datetime.datetime.now()
        db.session.commit()
        return 204
