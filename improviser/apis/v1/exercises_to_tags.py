import uuid

from apis.helpers import (
    get_range_from_args,
    get_sort_from_args,
    load,
    query_with_filters,
    save,
    update,
    get_filter_from_args,
)
from database import RiffExercise, RiffExerciseTag, Tag
from flask_restplus import Namespace, Resource, abort, fields, marshal_with
from flask_security import roles_accepted

api = Namespace("exercises-to-tags", description="Exercise to tag related operations")

exercise_to_tag_serializer = api.model(
    "ExerciseToTag",
    {
        "id": fields.String(),
        "tag_id": fields.String(required=True, description="Tag Id"),
        "riff_exercise_id": fields.String(required=True, description="Exercise Id"),
    },
)

parser = api.parser()
parser.add_argument("range", location="args", help="Pagination: default=[0,19]")
parser.add_argument("sort", location="args", help='Sort: default=["name","ASC"]')
parser.add_argument("filter", location="args", help="Filter default=[]")


@api.route("/")
@api.doc("Create tags")
class ExercisesToTagsResourceList(Resource):
    @marshal_with(exercise_to_tag_serializer)
    @api.doc(parser=parser)
    def get(self):
        """List tags for a exercise"""
        args = parser.parse_args()
        range = get_range_from_args(args)
        sort = get_sort_from_args(args, "id")
        filter = get_filter_from_args(args)

        query_result, content_range = query_with_filters(RiffExerciseTag, RiffExerciseTag.query, range, sort, filter)
        return query_result, 200, {"Content-Range": content_range}

    @roles_accepted("admin")
    @api.expect(exercise_to_tag_serializer)
    @api.marshal_with(exercise_to_tag_serializer)
    def post(self):
        """New ExerciseToTag"""
        # Todo: fix hook around me own weird id scheme...
        api.payload["riff_exercise_id"] = api.payload["exercise_id"]
        tag = Tag.query.filter(Tag.id == api.payload["tag_id"]).first()
        exercise = RiffExercise.query.filter(RiffExercise.id == api.payload["riff_exercise_id"]).first()

        if not tag or not exercise:
            abort(400, "Tag or exercise not found")

        check_query = RiffExerciseTag.query.filter_by(riff_exercise_id=exercise.id).filter_by(tag_id=tag.id).all()
        if len(check_query) > 0:
            abort(409, "Relation already exists")

        exercise_to_tag = RiffExerciseTag(id=str(uuid.uuid4()), riff_exercise=exercise, tag=tag)
        save(exercise_to_tag)

        return exercise_to_tag, 201


@api.route("/<id>")
@api.doc("ExerciseToTag detail operations.")
class ExercisesToTagsResource(Resource):
    @roles_accepted("admin")
    @marshal_with(exercise_to_tag_serializer)
    def get(self, id):
        """List ExerciseToTag"""
        item = load(RiffExerciseTag, id)
        return item, 200

    @roles_accepted("admin")
    @api.expect(exercise_to_tag_serializer)
    @api.marshal_with(exercise_to_tag_serializer)
    def put(self, id):
        """Edit ExerciseToTag"""
        item = load(RiffExerciseTag, id)
        item = update(item, api.payload)
        return item, 201
