import datetime
import re
from typing import List, Tuple

import structlog
from apis.helpers import get_range_from_args, get_sort_from_args, get_filter_from_args, query_with_filters
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

tag_info_marshaller = {
    "id": fields.String,
    "name": fields.String,
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
    'created_at': fields.DateTime,
    'tags': fields.Nested(tag_info_marshaller),
}

riff_detail_fields = {
    **riff_fields,
    'notes': fields.String,
}


riff_arguments = reqparse.RequestParser()
riff_arguments.add_argument('search_phrase', type=str, required=False,
                            help='Return only items that contain the search_phrase')

parser = api.parser()
parser.add_argument("range", location="args", help="Pagination: default=[0,19]")
parser.add_argument("sort", location="args", help='Sort: default=["name","ASC"]')
parser.add_argument("filter", location="args", help="Filter default=[]")


@api.route('/')
@api.doc("Show all riffs to users with sufficient rights. Provides the ability to filter on riff status and to search.")
class RiffResourceList(Resource):

    @roles_accepted('admin', 'moderator', 'member', 'student', 'teacher')
    @marshal_with(riff_fields)
    @api.expect(riff_arguments)
    def get(self):
        args = parser.parse_args()
        range = get_range_from_args(args)
        sort = get_sort_from_args(args)
        filter = get_filter_from_args(args)

        query_result, content_range = query_with_filters(
            Riff,
            Riff.query,
            range,
            sort,
            filter,
            quick_search_columns=["name", "id"]
        )

        # TODO: determine if we can live with unrendered riffs?
        # riffs_query = riffs_query.filter(Riff.render_valid)

        for riff in query_result:
            riff.tags = [{"id": tag.id, "name": tag.tag.name} for tag in riff.riff_to_tags]
            riff.image = f"https://www.improviser.education/static/rendered/120/riff_{riff.id}_c.png"
        return query_result, 200, {"Content-Range": content_range}

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

    @roles_accepted('admin', 'moderator', 'member', 'student', 'teacher')
    @marshal_with(riff_detail_fields)
    def get(self, riff_id):
        # Todo: check if riff is scaletrainer related otherwise block it for unauthorized users
        try:
            riff = Riff.query.filter(Riff.id == riff_id).first()
        except:
            abort(404, "riff not found")
        riff.tags = [{"id": tag.id, "name": tag.tag.name} for tag in riff.riff_to_tags]
        riff.image = f"https://www.improviser.education/static/rendered/120/riff_{riff.id}_c.png"
        # Todo: add an parameter to the endpoint to show extended music_xml info or move to separate endpoint
        # result = []
        # for octave in OCTAVES:
        #     result += [{"key_octave": key if not octave else f"{key}_{octave}",
        #                 "music_xml": convertToMusicXML(riff.notes, key)} for key in KEYS]
        # riff.music_xml_info = result
        return riff

    @roles_accepted('admin', 'moderator', 'teacher')
    @api.expect(riff_serializer)
    def put(self, riff_id):
        riff = Riff.query.filter_by(id=riff_id).first()
        # Todo implement real update
        return 204


@api.route('/unrendered')
@api.doc("Show all unrendered riffs to users with sufficient rights.")
class UnrenderedRiffResourceList(Resource):

    @quick_token_required
    @roles_accepted('admin', 'moderator')
    @marshal_with(riff_detail_fields)
    def get(self):
        return Riff.query.filter(Riff.render_valid.is_(False)).all()


@api.route('/rendered/<string:riff_id>')
class RiffResourceRendered(Resource):

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
        filter_parameters = []
        if filters.count(",") == 1:
            logger.info("Preparing single column filter")
            filter_parameters.append(filters)
        else:
            logger.info("Preparing multi column filter")
            filter_parameters = re.findall("[^,]+,[^,]+", filters)
        try:
            for parameter in filter_parameters:
                field, value = parameter.split(",")
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

    if sort:
        sort_parameters = []
        if sort.count(",") == 1:
            logger.info("Preparing single column sort")
            sort_parameters.append(sort)
        else:
            logger.info("Preparing multi column sort")
            sort_parameters = re.findall("[^,]+,[^,]+", sort)
        try:
            for parameter in sort_parameters:
                field, value = parameter.split(",")
                # Todo: implement sort on tag
                import sqlalchemy.sql.expression as sql_expressions
                if value.upper() == 'DESC':
                    query = query.order_by(sql_expressions.desc(Riff.__dict__[field]))
                else:
                    query = query.order_by(sql_expressions.asc(Riff.__dict__[field]))
        except Exception as error:
            logger.error("Error while handling sort", sort=sort, error=error)

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
