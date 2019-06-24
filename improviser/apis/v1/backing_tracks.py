import datetime
from database import db
from flask import request
from flask_restplus import Namespace, Resource, fields, marshal_with, reqparse, abort
from database import BackingTrack


api = Namespace("backing tracks", description="BackingTrack related operations")

backing_track_serializer = api.model("BackingTrack", {
    "name": fields.String(required=True, description="Name"),
    "chord_info": fields.String(description="Chord info in lilypond format"),
    "tempo": fields.Integer(description="Tempo in BPM [40-320]"),
'c_available': fields.Boolean(), 'cis_available': fields.Boolean(), 'd_available': fields.Boolean(), 'ees_available': fields.Boolean(),
                     'e_available': fields.Boolean(), 'f_available': fields.Boolean(), 'fis_available': fields.Boolean(), 'g_available': fields.Boolean(),
                     'aes_available': fields.Boolean(), 'a_available': fields.Boolean(),
                     'bes_available': fields.Boolean(), 'b_available': fields.Boolean()
})


backing_track_arguments = reqparse.RequestParser()
backing_track_arguments.add_argument('search_phrase', type=str, required=False,
                            help='Return only items that contain the search_phrase')

@api.route('/')
class BackingTrackResourceList(Resource):

    @marshal_with(backing_track_serializer)
    @api.expect(backing_track_arguments)
    def get(self):
        args = request.args
        return BackingTrack.query.all(), 200

    @api.expect(backing_track_serializer)
    def post(self):
        return 501