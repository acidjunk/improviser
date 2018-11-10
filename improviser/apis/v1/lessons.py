import datetime
from database import db_session
from flask import request
from flask_restplus import Namespace, Resource, fields, marshal_with, reqparse, abort
from models import RiffExercise


api = Namespace("lessons", description="Lesson related operations")

lesson_serializer = api.model("Exercise", {
    "name": fields.String(required=True, description="Name"),
    "description": fields.String(description="Description as shown in the lesson list and overviews")
})


lesson_arguments = reqparse.RequestParser()
lesson_arguments.add_argument('search_phrase', type=str, required=False,
                            help='Return only items that contain the search_phrase')

@api.route('/')
class LessonResourceList(Resource):

    @marshal_with(lesson_serializer)
    @api.expect(lesson_arguments)
    def get(self):
        args = request.args
        # lessons = lesson_query.all()
        return 501

    @api.expect(lesson_serializer)
    def post(self):
        return 501

