# coding:utf-8
import datetime
from flask import Blueprint
from flask import render_template, request
from flask_restplus import Resource, marshal_with, abort, fields, reqparse, Namespace

from .models import *

app = Blueprint('blueprint', __name__,
    template_folder='templates')

api = Namespace('riffs', description='Riffs related')

riff_serializer = api.model('Riff', {
    'name': fields.String(required=True, description='Unique riff name'),
    'number_of_bars': fields.Integer(required=True, description='Number of bars'),
    'notes': fields.String(required=True, description='Lilypond representation of the riff'),
    'chord': fields.String(description='Chord if known'),
})

riff_render_serializer = api.model('Riff', {
    'render_valid': fields.Boolean(required=True, description='Whether a render is deemed valid.'),
})

riff_exercise_serializer = api.model('RiffExercise', {
    'name': fields.String(required=True, description='Unique exercise name'),
    'is_global': fields.Boolean(description="Is this riff exercise visible to everyone?", default=False),
})

# Todo: make this a nested list: so order can be dealt with easily
riff_exercise_item_serializer = api.model('RiffExerciseItem', {
    'riff_exercise_id': fields.String(required=True, description='Unique exercise name'),
    'riff_id': fields.Boolean(description="Is this riff exercise visible to everyone?"),
})


riff_fields = {
    'id': fields.String,
    'difficulty': fields.String,
    'name': fields.String,
    'number_of_bars': fields.Integer,
    'notes': fields.String,
    'notes_abc': fields.String(description='ABC representation of the riff (computed)'),
    'chord': fields.String,
    'image': fields.String,
    'render_valid': fields.Boolean,
    'render_date': fields.DateTime,
}

riff_exercise_fields = {
    'id': fields.String,
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


@api.route('/')
class RiffResourceList(Resource):

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
            riff.notes_abc = f"{convertToMusicXML(riff.notes)}"
            riff.image = f"https://www.improviser.education/static/rendered/large/riff_{riff.id}_c.png"
        return riffs

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

    @marshal_with(riff_fields)
    def get(self, riff_id):
        riff = Riff.query.filter_by(id=riff_id).first_or_404()
        riff.image = f"https://www.improviser.education/static/rendered/large/riff_{riff.id}_c.png"
        riff.notes_abc = f"abc"
        return riff

    @api.expect(riff_serializer)
    def put(self, riff_id):
        riff = Riff.query.filter_by(id=riff_id).first_or_404()
        # Todo implement real update
        return 204


@api.route('/rendered/<string:riff_id>')
class RiffResourceRendered(Resource):
    @api.expect(riff_render_serializer)
    def put(self, riff_id):
        riff = Riff.query.filter_by(id=riff_id).first_or_404()
        riff.render_valid = api.payload["render_valid"]
        riff.render_date = datetime.datetime.now()
        db.session.commit()
        return 204


@api.route('/exercises')
class RiffExerciseResourceList(Resource):

    @marshal_with(riff_exercise_fields)
    @api.expect(riff_exercise_arguments)
    def get(self):
        args = request.args
        # handle case insensitive search
        if args.get("search_phrase"):
            riff_exercises_query = RiffExercise.query.filter(RiffExercise.name.ilike('%' + args["search_phrase"] + '%'))
        else:
            riff_exercises_query = RiffExercise.query

        # todo: filter on created_by and is_global
        return riff_exercises_query.all()

    @api.expect(riff_exercise_serializer)
    def post(self):
        """A new riff is always just a name. Note Riff Items will be added via update..."""
        riff_exercise = RiffExercise(**api.payload)
        # Todo: add user
        try:
            db.session.add(riff_exercise)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            abort(400, 'DB error: {}'.format(str(error)))
        return 201


@api.route('/exercises/<string:riff_exercise_id>')
class RiffExerciseResource(Resource):
    @api.expect(riff_exercise_serializer)
    def put(self, riff_exercise_id):
        riff_exercise = RiffExercise.query.filter_by(id=riff_exercise_id).first_or_404()
        riff_exercise.name = api.payload["name"]
        riff_exercise.is_global = api.payload["name"]
        # Todo: add items also.

        db.session.commit()
        return 204

    @marshal_with(riff_exercise_fields)
    def get(self, riff_exercise_id):
        riff_exercise = RiffExercise.query.filter_by(id=riff_exercise_id).first_or_404()
        # Todo: do stuff with items also.
        return riff_exercise

