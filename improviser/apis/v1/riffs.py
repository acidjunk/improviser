import datetime
import re
import uuid
from copy import copy
from typing import List, Tuple

import structlog
from apis.helpers import (
    get_range_from_args,
    get_sort_from_args,
    get_filter_from_args,
    query_with_filters,
    save,
    load,
    update,
)
from database import db
from flask import request
from flask_login import current_user
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

riff_serializer = api.model(
    "Riff",
    {
        "id": fields.String(),
        "name": fields.String(required=True, description="Unique riff name"),
        "number_of_bars": fields.Integer(required=True, description="Number of bars"),
        "notes": fields.String(required=True, description="Lilypond representation of the riff"),
        "chord": fields.String(description="Chord if known"),
        "multi_chord": fields.Boolean(description="Multiple chords in this riff?"),
        "scale_trainer_enabled": fields.Boolean(description="Show this riff in the scale trainer?"),
        "chord_info": fields.String(),
    },
)

riff_render_serializer = api.model(
    "RenderedRiff",
    {
        "render_valid": fields.Boolean(required=True, description="Whether a render is deemed valid."),
        "image_info": fields.String(description="The metainfo for all images for this riff, per key, octave"),
    },
)

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
    "id": fields.String,
    "difficulty": fields.String,
    "name": fields.String,
    "number_of_bars": fields.Integer,
    "chord_info": fields.String,
    "chord": fields.String,
    "multi_chord": fields.Boolean,
    "image": fields.String,
    "image_info": fields.Nested(image_info_marshaller),
    "render_valid": fields.Boolean,
    "render_date": fields.DateTime,
    "created_at": fields.DateTime,
    "tags": fields.Nested(tag_info_marshaller),
}

riff_detail_fields = {
    **riff_fields,
    "notes": fields.String,
}


riff_arguments = reqparse.RequestParser()
riff_arguments.add_argument(
    "search_phrase", type=str, required=False, help="Return only items that contain the search_phrase"
)

parser = api.parser()
parser.add_argument("range", location="args", help="Pagination: default=[0,19]")
parser.add_argument("sort", location="args", help='Sort: default=["name","ASC"]')
parser.add_argument("filter", location="args", help="Filter default=[]")


@api.route("/")
@api.doc("Show all riffs to users with sufficient rights. Provides the ability to filter on riff status and to search.")
class RiffResourceList(Resource):
    @roles_accepted("admin", "moderator", "member", "student", "teacher")
    @marshal_with(riff_fields)
    @api.expect(riff_arguments)
    def get(self):
        args = parser.parse_args()
        range = get_range_from_args(args)
        sort = get_sort_from_args(args)
        filter = get_filter_from_args(args)

        riffs_query = Riff.query
        if "admin" not in current_user.roles:
            riffs_query = riffs_query.filter(Riff.render_valid)
        else:
            logger.debug(
                "Showing unrendered riffs for non admin user",
                user_id=current_user.id,
                roles=[role.name for role in current_user.roles],
            )

        query_result, content_range = query_with_filters(
            Riff, riffs_query, range, sort, filter, quick_search_columns=["name", "id"]
        )

        for riff in query_result:
            riff.tags = [{"id": tag.id, "name": tag.tag.name} for tag in riff.riff_to_tags]
            riff.image = f"https://www.improviser.education/static/rendered/120/riff_{riff.id}_c.png"
        return query_result, 200, {"Content-Range": content_range}

    @roles_accepted("admin", "moderator", "teacher")
    @api.expect(riff_serializer)
    @api.marshal_with(riff_serializer)
    def post(self):
        riff = Riff(id=str(uuid.uuid4()), **api.payload)
        save(riff)
        print(riff)
        return riff, 201


@api.route("/<string:id>")
class RiffResource(Resource):
    @roles_accepted("admin", "moderator", "member", "student", "teacher")
    @marshal_with(riff_detail_fields)
    def get(self, id):
        # Todo: check if riff is scaletrainer related otherwise block it for unauthorized users
        try:
            riff = Riff.query.filter(Riff.id == id).first()
        except:
            abort(404, "riff not found")

        riff_copy = copy(riff)
        riff_copy.tags = [{"id": tag.id, "name": tag.tag.name} for tag in riff.riff_to_tags]
        riff_copy.image = f"https://www.improviser.education/static/rendered/120/riff_{riff.id}_c.png"

        if "admin" not in current_user.roles:
            logger.debug(
                "Disabling notes for non admin user",
                user_id=current_user.id,
                roles=[role.name for role in current_user.roles],
            )
            riff_copy.notes = ""

        # Todo: add an parameter to the endpoint to show extended music_xml info or move to separate endpoint
        # result = []
        # for octave in OCTAVES:
        #     result += [{"key_octave": key if not octave else f"{key}_{octave}",
        #                 "music_xml": convertToMusicXML(riff.notes, key)} for key in KEYS]
        # riff.music_xml_info = result
        return riff_copy

    @roles_accepted("admin", "moderator")
    @api.expect(riff_serializer)
    @api.marshal_with(riff_serializer)
    def put(self, id):
        """Edit Tag"""
        item = load(Riff, id)
        item = update(item, api.payload)
        return item, 201


@api.route("/unrendered")
@api.doc("Show all unrendered riffs to users with sufficient rights.")
class UnrenderedRiffResourceList(Resource):
    @roles_accepted("admin", "moderator")
    @marshal_with(riff_detail_fields)
    def get(self):
        return Riff.query.filter(Riff.render_valid.is_(False)).all()


@api.route("/rendered/<string:id>")
class RiffResourceRendered(Resource):
    @roles_accepted("admin")
    @api.expect(riff_render_serializer)
    def put(self, id):
        riff = Riff.query.filter_by(id=id).first()
        riff.render_valid = api.payload["render_valid"]
        riff.image_info = api.payload["image_info"]
        riff.render_date = datetime.datetime.now()
        db.session.commit()
        return 204
