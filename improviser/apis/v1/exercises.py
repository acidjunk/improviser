import datetime
from .riffs import riff_fields

from database import db_session
from flask import request
from flask_restplus import Namespace, Resource, fields, marshal_with, reqparse, abort
from models import Riff, RiffExercise


api = Namespace("exercises", description="Exercise related operations")

exercise_serializer = api.model("Exercise", {
    "name": fields.String(required=True, description="Name"),
    "rootPitch": fields.String(description="rootPitch of this exercise, needed for HQ render of complete exercise")
})


exercise_arguments = reqparse.RequestParser()
exercise_arguments.add_argument('search_phrase', type=str, required=False,
                            help='Return only items that contain the search_phrase')

@api.route('/')
class ExerciseResourceList(Resource):

    @marshal_with(exercise_serializer)
    @api.expect(exercise_arguments)
    def get(self):
        args = request.args
        # handle case insensitive search
        if args.get("search_phrase"):
            exercise_query = RiffExercise.query.filter(RiffExercise.name.ilike('%' + args["search_phrase"] + '%'))
        else:
            exercise_query = RiffExercise.query

        exercises = exercise_query.all()
        return exercises

    @api.expect(exercise_serializer)
    def post(self):
        exercise = RiffExercise(**api.payload)
        try:
            db_session.add(exercise)
            db_session.commit()
        except Exception as error:
            db_session.rollback()
            abort(400, 'DB error: {}'.format(str(error)))
        return 201


@api.route('/scales')
class ScaleTrainerResourceList(Resource):

    @marshal_with(riff_fields)
    def get(self):
        #Todo: query riffs that are allowed in scaletrainer
        riffs = Riff.query.filter(Riff.number_of_bars==1 or Riff.number_of_bars==2).all()
        return riffs
