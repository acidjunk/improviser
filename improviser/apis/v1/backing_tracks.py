import datetime
import uuid

import structlog
from apis.helpers import (
    get_range_from_args,
    get_sort_from_args,
    get_filter_from_args,
    query_with_filters,
    load,
    upload_file,
    update,
    save,
)
from flask import request
from flask_restx import Namespace, Resource, fields, marshal_with, reqparse, abort
from database import BackingTrack, RiffExercise
from flask_security import roles_accepted
from werkzeug.datastructures import FileStorage

logger = structlog.get_logger(__name__)

api = Namespace("backing tracks", description="BackingTrack related operations")

backing_track_serializer = api.model(
    "BackingTrack",
    {
        "id": fields.String(),
        "name": fields.String(required=True, description="Name"),
        "chord_info": fields.String(description="Chord info in lilypond format"),
        "number_of_bars": fields.Integer(description="Number of bars (chord loop length"),  # Todo: derive from chords
        "tempo": fields.Integer(description="Tempo in BPM [40-320]"),
        "file": fields.String(description="Backing track mp3"),
        "approved": fields.Boolean(description="Approve toggle for admins"),
    },
)



backing_track_fields = {
    "id": fields.String,
    "name": fields.String,
    "chord_info": fields.String,
    "number_of_bars": fields.Integer,  # loop length
    "tempo": fields.Integer,
    "file": fields.String,
    "created_at": fields.DateTime,
    "modified_at": fields.DateTime,
    "approved": fields.Boolean,
    "approved_at": fields.DateTime,
}

wizard_fields = {
    "full_match": fields.Nested(backing_track_fields),
    "fuzzy_match": fields.Nested(backing_track_fields),
}


parser = api.parser()
parser.add_argument("range", location="args", help="Pagination: default=[0,19]")
parser.add_argument("sort", location="args", help='Sort: default=["name","ASC"]')
parser.add_argument("filter", location="args", help="Filter default=[]")

file_upload = reqparse.RequestParser()
file_upload.add_argument("file", type=FileStorage, location="files", help="file")


@api.route("/")
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

        # todo: remove approved from payload: only approve on update...

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

        api.payload["modified_at"] = datetime.datetime.utcnow()
        if api.payload.get("approved"):
            if api.payload["approved"] and not item.approved:
                api.payload["approved_at"] = datetime.datetime.utcnow()
            if not api.payload["approved"] and item.approved:
                api.payload["approved_at"] = None

        data = request.get_json()
        backing_track_update = {}
        file_cols = ["file"]
        for file_col in file_cols:
            if data.get(file_col) and type(data[file_col]) == dict:
                name = f"{uuid.uuid4()}.mp3"
                upload_file(data[file_col]["src"], name)
                backing_track_update[file_col] = name
        item = update(item, {**api.payload, **backing_track_update})

        return item, 201


@api.route("/for/<exercise_id>")
class BackingTrackWizardResourceList(Resource):
    @roles_accepted("admin", "moderator", "member", "student", "teacher")
    @marshal_with(wizard_fields)
    def get(self, exercise_id):
        """

        First check if a backing track is found that matches total length of exercise
        Then check if backing tracks can be found for COMMON_MULTIPLIERS that match the beginning of this song

        """

        COMMON_MULTIPLIERS = [1, 2, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 64, 68, 72, 76, 80]

        exercise = load(RiffExercise, exercise_id)

        # TODO:
        # convert all flats / "es" to sharps / "is"

        chords = exercise.get_normalised_chord_info
        chords_string = " ".join(chords)
        number_of_bars = 0
        for item in exercise.riff_exercise_items:
            number_of_bars += item.number_of_bars
        number_of_chords = len(chords)

        print("\n*********************************")
        print("**  Doing backing track stuff  **")
        print("*********************************")
        print("\nChord Info in selected exercise:")
        print("--------------------------------")
        print(
            f"number_of_bars: {number_of_bars}\n"
            f"umber_of_chords: {len(chords)}\n"
            f"number_of_items: {len(exercise.riff_exercise_items)}\n"
            f"chords: {chords}\n"
        )
        # Todo : implement a first simple version

        print("\nSearching for full match:")
        print("--------------------------------")
        full_match = BackingTrack.query.filter(BackingTrack.chord_info == chords_string).all()

        print(
            f"complete chord string: {chords_string}\n"
            f"results: {[bt.name for bt in full_match]}\n")

        # For now return all backing tracks
        fuzzy_match = BackingTrack.query.all()
        return {"full_match": full_match, "fuzzy_match": fuzzy_match}, 200
