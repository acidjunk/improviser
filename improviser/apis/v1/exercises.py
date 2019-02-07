import uuid
import structlog

from flask_login import current_user
from flask_security import roles_accepted
from security import quick_token_required

from flask import request
from flask_restplus import Namespace, Resource, fields, marshal_with, reqparse, abort

from database import db, Riff, RiffExercise, RiffExerciseItem
from .riffs import riff_fields

logger = structlog.get_logger(__name__)

api = Namespace("exercises", description="Exercise related operations")

exercise_list_serializer = api.model("RiffExercise", {
    "id": fields.String(required=True),
    "name": fields.String(required=True, description="Unique exercise name"),
    "description": fields.String(required=True, description="Description", default=False),
    "is_public": fields.Boolean(required=True, description="Is this riff exercise visible to everyone?", default=False),
    "root_key": fields.String(required=True, description="Root key of exercise (for printing purposes in the future)", default=False),
    "created_at": fields.DateTime(),
    "created_by": fields.String(),
    "gravatar_image": fields.String(),
    "tags": fields.List(fields.String),
})

exercise_item_serializer = api.model("RiffExerciseItem", {
    "riff_exercise_id": fields.String(required=True, description="Unique exercise name"),
    "pitch": fields.String(required=True),
    "octave": fields.Integer(required=True),
    "order_number": fields.Integer(required=True),
    "chord_info": fields.String(required=False),  # when NOT provided; the chord info of the riffs will be used
    "riff_id": fields.String(required=True, description="The riff"),
    "created_at": fields.DateTime(),
})

exercise_detail_serializer = api.model("RiffExercise", {
    "name": fields.String(required=True, description="Unique exercise name"),
    "description": fields.String(required=True, description="Description", default=False),
    "is_public": fields.Boolean(required=True, description="Is this riff exercise visible to everyone?", default=False),
    "root_key": fields.String(required=True, description="Root key of exercise (for printing purposes in the future)", default=False),
    "created_at": fields.DateTime(),
    "created_by": fields.String(),
    "gravatar_image": fields.String(),
    "tags": fields.List(fields.String),
    "exercise_items": fields.Nested(exercise_item_serializer),
    "riffs": fields.Nested(riff_fields)
})

exercise_item_fields = {
    # "riff_exercise_id": fields.String(required=True, description="Unique exercise name"),
    "pitch": fields.String(required=True),
    "octave": fields.Integer(required=True),
    "order_number": fields.Integer(required=True),
    "riff_id": fields.String(required=True, description="The riff"),
}

exercise_fields = {
    "name": fields.String,
    "description": fields.String,
    "root_key": fields.String,
    "is_public": fields.Boolean,
    "created_at": fields.DateTime,
    "created_by": fields.String,
    "exercise_items": fields.Nested(exercise_item_fields),

}

exercise_detail_fields = exercise_fields
# exercise_detail_fields["riffs"] = fields.List(fields.Nested(riff_fields))


exercise_arguments = reqparse.RequestParser()
exercise_arguments.add_argument('search_phrase', type=str, required=False,
                                help='Return only items that contain the search_phrase')

exercise_message_fields = {
   'available': fields.Boolean,
   'reason': fields.String,
}


@api.route('/validate-exercise-name/<string:name>')
class ValidateExerciseNameResource(Resource):

    @quick_token_required
    def get(self, name):
        print(current_user)

        exercise = RiffExercise.query.filter(RiffExercise.name == name)\
            .filter(RiffExercise.user == current_user).first()
        if not exercise:
            return {'available': True, 'reason': ''}
        else:
            return {'available': False, 'reason': 'This exercise name already exists for the current user'}


@api.route('/')
class ExerciseResourceList(Resource):

    @marshal_with(exercise_list_serializer)
    @api.expect(exercise_arguments)
    def get(self):
        args = request.args
        # handle case insensitive search
        if args.get("search_phrase"):
            exercise_query = RiffExercise.query.filter(RiffExercise.name.ilike('%' + args["search_phrase"] + '%'))
        else:
            exercise_query = RiffExercise.query

        exercises = exercise_query.all()

        for exercise in exercises:
            exercise.tags = [str(tag.name) for tag in exercise.riff_exercise_tags]

        return exercises

    @quick_token_required
    @roles_accepted('admin', 'moderator', 'member')
    @api.expect(exercise_fields)
    def post(self):
        exercise_items = api.payload.pop("exercise_items", [])
        exercise = RiffExercise(**api.payload, created_by=current_user.id)
        try:
            db.session.add(exercise)
            for exercise_item in exercise_items:
                chord_info = exercise_item.get("chord_info")
                if not chord_info:
                    # Try retrieving it from the riff itself
                    riff = Riff.query.filter(Riff.id == exercise_item["riff_id"]).first()
                    chord_info = riff.chord_info if riff.chord_info else riff.chord
                    # Todo: handle tranpose correctly
                else:
                    # Todo: validate user stuff
                    pass
                if chord_info:
                    exercise_item["chord_info"] = chord_info
                logger.info("Adding item to exercise", item=exercise_item, exercise_id=api.payload['id'])

                #record = RiffExerciseItem(**exercise_item, id=str(uuid.uuid4()), riff_exercise_id=api.payload["id"])
            #     db.session.add(record)
            # db.session.commit()
        except Exception as error:
            db.session.rollback()
            logger.error("DB exercise add caused a rollback", error=error)
            abort(400, 'DB error: {}'.format(str(error)))
        return 201


@api.route('/<string:exercise_id>')
class ExerciseResource(Resource):

    @marshal_with(exercise_detail_serializer)
    def get(self, exercise_id):
        # Todo: check if riff is scaletrainer related otherwise block it for unauthorized users
        exercise = RiffExercise.query.filter(RiffExercise.id == exercise_id).first()
        exercise.tags = [str(tag.name) for tag in exercise.riff_exercise_tags]

        # Include riffs used in the exercise in the response
        riffs = []


        return exercise












@api.route('/scales')
class ScaleTrainerResourceList(Resource):

    @marshal_with(riff_fields)
    def get(self):
        #Todo: query riffs that are allowed in scaletrainer
        riffs = Riff.query.filter(Riff.scale_trainer_enabled).all()
        return riffs
