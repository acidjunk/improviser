import datetime
import uuid

import structlog
from apis.helpers import (
    get_range_from_args, get_sort_from_args, get_filter_from_args, query_with_filters, load,
    name_file,
    upload_file,
    update,
    save
)
from database import db
from flask import request
from flask_restplus import Namespace, Resource, fields, marshal_with, reqparse, abort
from database import BackingTrack
from flask_security import roles_accepted
from werkzeug.datastructures import FileStorage

logger = structlog.get_logger(__name__)

api = Namespace("backing tracks", description="BackingTrack related operations")

backing_track_serializer = api.model("BackingTrack", {
    "name": fields.String(required=True, description="Name"),
    "chord_info": fields.String(description="Chord info in lilypond format"),
    "tempo": fields.Integer(description="Tempo in BPM [40-320]"),
    "file": fields.Integer(description="Backing track mp3"),
})

backing_track_fields = {
    'id': fields.String,
    'name': fields.String,
    'chord_info': fields.String,
    'file': fields.String,
    'complete': fields.Boolean,
    'created_at': fields.DateTime,
}

parser = api.parser()
parser.add_argument("range", location="args", help="Pagination: default=[0,19]")
parser.add_argument("sort", location="args", help='Sort: default=["name","ASC"]')
parser.add_argument("filter", location="args", help="Filter default=[]")

file_upload = reqparse.RequestParser()
file_upload.add_argument("file", type=FileStorage, location="files", help="file")

@api.route('/')
class BackingTrackResourceList(Resource):

    @roles_accepted("admin")
    @marshal_with(backing_track_fields)
    @api.doc(parser=parser)
    def get(self):
        args = parser.parse_args()
        range = get_range_from_args(args)
        sort = get_sort_from_args(args)
        filter = get_filter_from_args(args)

        query_result, content_range = query_with_filters(
            BackingTrack,
            BackingTrack.query,
            range,
            sort,
            filter,
            quick_search_columns=["name", "file", "tempo"],
        )

        return query_result, 200, {"Content-Range": content_range}

    @roles_accepted("admin")
    @marshal_with(backing_track_serializer)
    @api.expect(file_upload)
    def post(self):
        args = file_upload.parse_args()
        logger.warning("Ignoring files via args! (using JSON body)", args=args)

        data = request.get_json()
        backing_track = BackingTrack(id=str(uuid.uuid4()), **api.payload)

        if data.get("file") and type(data["file"]) == dict:
            name = f"{uuid.uuid4()}.mp3"
            upload_file(data["file"]["src"], name)
            backing_track.file = name
        save(backing_track)
        return backing_track, 201


@api.route("/<id>")
@api.doc("Backing track detail operations.")
class BackingTrackResource(Resource):
    @roles_accepted("admin")
    @marshal_with(backing_track_fields)
    def get(self, id):
        """List Image"""
        item = load(BackingTrack, id)
        return item, 200


    @roles_accepted("admin")
    @marshal_with(backing_track_serializer)
    @api.expect(file_upload)
    def put(self, id):
        args = file_upload.parse_args()
        logger.warning("Ignoring files via args! (using JSON body)", args=args)
        item = load(BackingTrack, id)
        # todo: raise 404 o abort

        data = request.get_json()
        backing_track_update = {}
        file_cols = ["file"]
        for file_col in file_cols:
            if data.get(file_col) and type(data[file_col]) == dict:
                name = f"{uuid.uuid4()}.mp3"
                upload_file(data[file_col]["src"], name)  # todo: use mime-type in first part of
                backing_track_update[file_col] = name
        item = update(item, backing_track_update)

        return item, 201
