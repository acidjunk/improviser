import datetime
from typing import List, Tuple

import structlog
from database import db
from flask import request
from flask_restplus import Namespace, Resource, fields, marshal_with, reqparse, abort
from database import Riff
from flask_security import auth_token_required, roles_accepted
from more_itertools import chunked
from security import quick_token_required
from sqlalchemy import cast, String

logger = structlog.get_logger(__name__)

KEYS = ["c", "cis", "d", "dis", "ees", "e", "f", "fis", "g", "gis", "aes", "a", "ais", "bes", "b"]
OCTAVES = [-1, 0, 1, 2]

api = Namespace("riffs", description="Riff related operations")

riff_serializer = api.model("Riff", {
    "name": fields.String(required=True, description="Unique riff name"),
    "number_of_bars": fields.Integer(required=True, description="Number of bars"),
    "notes": fields.String(required=True, description="Lilypond representation of the riff"),
    "chord": fields.String(description="Chord if known"),
    "multi_chord": fields.Boolean(description="Multiple chords in this riff?"),
    "scale_trainer_enabled": fields.Boolean(description="Show this riff in the scale trainer?"),
    "chord_info": fields.String(),
})

riff_render_serializer = api.model("RenderedRiff", {
    "render_valid": fields.Boolean(required=True, description="Whether a render is deemed valid."),
    "image_info": fields.String(description="The metainfo for all images for this riff, per key, octave")
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

riff_detail_fields = {
    **riff_fields,
    'notes': fields.String,
}

riff_arguments = reqparse.RequestParser()
riff_arguments.add_argument('search_phrase', type=str, required=False,
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

    @quick_token_required
    @roles_accepted('admin', 'moderator', 'member', 'student', 'teacher')
    @marshal_with(riff_fields)
    @api.expect(riff_arguments)
    def get(self):
        args = request.args
        # handle case insensitive search
        search_phrase = args.get("search_phrase")
        range_param = args.get("range")
        sort_param = args.get("sort")
        filter_param = args.get("filter")

        logger.info("Getting riffs", filter=filter_param, range=range_param, search_phrase=search_phrase, sort=sort_param)

        if search_phrase:
            riffs_query = Riff.query.filter(Riff.name.ilike('%' + search_phrase + '%') |
                                            cast(Riff.id, String).startswith(search_phrase))
        else:
            riffs_query = Riff.query

        riffs_query = riffs_query.filter(Riff.render_valid)

        riffs, headers = _query_with_filters(query=riffs_query, range=range_param, sort=sort_param, filters=filter_param)

        # Todo: load tags with contains eager?
        # For now nog server sided tags filter
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


@api.route('/unrendered')
@api.doc("Show all unrendered riffs to users with sufficient rights.")
class UnrenderedRiffResourceList(Resource):

    @quick_token_required
    @roles_accepted('admin', 'moderator')
    @marshal_with(riff_detail_fields)
    def get(self):
        return Riff.query.filter(Riff.render_valid.is_(False)).all()


@api.route('/<string:riff_id>')
class RiffResource(Resource):

    @marshal_with(riff_detail_fields)
    def get(self, riff_id):
        # Todo: check if riff is scaletrainer related otherwise block it for unauthorized users
        riff = Riff.query.filter(Riff.id == riff_id).first()
        riff.tags = [str(tag.name) for tag in riff.riff_tags]
        riff.image = f"https://www.improviser.education/static/rendered/120/riff_{riff.id}_c.png"
        # Todo: add an parameter to the endpoint to show extended music_xml info or move to separate endpoint
        # result = []
        # for octave in OCTAVES:
        #     result += [{"key_octave": key if not octave else f"{key}_{octave}",
        #                 "music_xml": convertToMusicXML(riff.notes, key)} for key in KEYS]
        # riff.music_xml_info = result
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


def _query_with_filters(query,
                        range=None,
                        sort=None,
                        filters=None):
    """
    Returns filters that can be applied to a existing Riff.query.all() object to get filtered an sorted results
    :param query:
    :param range:
    :param sort:
    :param filters:

    :return: QueryFilters + Header !
    """
    headers = {}

    # Todo: handle list of filters also
    if filters:
        try:
            filter = filters.split(",")
            print(filter)
            field = filter[0]
            value = filter[1]
            if field.endswith('_gt'):
                query = query.filter(Riff.__dict__[field[:-3]] > value)
            elif field.endswith('_gte'):
                query = query.filter(Riff.__dict__[field[:-4]] >= value)
            elif field.endswith('_lte'):
                query = query.filter(Riff.__dict__[field[:-4]] <= value)
            elif field.endswith('_lt'):
                query = query.filter(Riff.__dict__[field[:-3]] < value)
            elif field.endswith('_ne'):
                query = query.filter(Riff.__dict__[field[:-3]] != value)
            elif field == "name":
                query = query.filter(Riff.name.ilike('%' + value + '%'))
            elif field == "chord":
                query = query.filter(Riff.chord.ilike('%' + value + '%'))
            elif field == "riff.tags":
                pass
            else:
                query = query.filter(cast(Riff.__dict__[field], String).startswith(value))
        except Exception as error:
            logger.error("Error while handling filter", filter=filter, error=error)

    if sort is not None and len(sort) >= 2:
        for sort in chunked(sort, 2):
            # Todo: implement sort on tag
            if sort and len(sort) == 2:
                import sqlalchemy.sql.expression as sql_expressions
                if sort[1].upper() == 'DESC':
                    query = query.order_by(sql_expressions.desc(Riff.__dict__[sort[0]]))
                else:
                    query = query.order_by(sql_expressions.asc(Riff.__dict__[sort[0]]))

    if range:
        try:
            range = range.split(",")
            range_start = int(range[0])
            range_end = int(range[1])
        except Exception as error:
            logger.error("Error while handling range", range=range, error=error)
            # Todo: show max 5 when user is fiddling with range
            range_start = 0
            range_end = 4

        # Range is inclusive so we need to add one
        range_length = max(range_end - range_start + 1, 0)

        total = query.count()
        query = query.offset(range_start)
        query = query.limit(range_length)
    else:
        range_start = 0
        range_end = 50
        # Range is inclusive so we need to add one
        range_length = max(range_end - range_start + 1, 0)
        total = query.count()
        query = query.offset(range_start)
        query = query.limit(range_length)

    headers["Content-Range"] = f"Riffs {range_start}-{range_end}/{total}"

    return query.all(), headers
