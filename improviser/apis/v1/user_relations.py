import uuid

from apis.helpers import (
    get_range_from_args,
    get_sort_from_args,
    load,
    query_with_filters,
    save,
    update,
    delete,
    get_filter_from_args,
)
from database import UserRelation, User
from flask_restx import Namespace, Resource, abort, fields, marshal_with
from flask_security import roles_accepted
from flask_login import current_user

api = Namespace("user_relations", description="User Relation related operations")

user_relation_serializer = api.model(
    "User Relation",
    {
        "id": fields.String(),
        "school_id": fields.String(),
        "owner_id": fields.String(),
        "teacher_id": fields.String(),
        "student_id": fields.String(),
    },
)

parser = api.parser()
parser.add_argument("range", location="args", help="Pagination: default=[0,19]")
parser.add_argument("sort", location="args", help='Sort: default=["name","ASC"]')
parser.add_argument("filter", location="args", help="Filter default=[]")


@api.route("/")
@api.doc("Create user relations")
class SchoolsResourceList(Resource):
    @marshal_with(user_relation_serializer)
    @api.doc(parser=parser)
    def get(self):
        """List User Relations"""
        args = parser.parse_args()
        range = get_range_from_args(args)
        sort = get_sort_from_args(args, "id")
        filter = get_filter_from_args(args)

        query_result, content_range = query_with_filters(UserRelation, UserRelation.query, range, sort, filter)
        return query_result, 200, {"Content-Range": content_range}

    @roles_accepted("admin")
    @api.expect(user_relation_serializer)
    @api.marshal_with(user_relation_serializer)
    def post(self):
        owner = User.query.filter(User.id == api.payload["owner_id"]).first()
        teacher = User.query.filter(User.id == api.payload["teacher_id"]).first()
        student = User.query.filter(User.id == api.payload["student_id"]).first()

        if not owner or not teacher or not student:
            abort(400, "User(s) not found")

        relation = UserRelation(id=str(uuid.uuid4()), **api.payload, created_by=str(current_user.id))

        save(relation)
        return relation, 201


@api.route("/<id>")
@api.doc("User Relation detail operations.")
class RiffsToTagsResource(Resource):
    @roles_accepted("admin")
    @marshal_with(user_relation_serializer)
    def get(self, id):
        """List User Relation"""
        item = load(UserRelation, id)
        return item, 200

    @roles_accepted("admin")
    @api.expect(user_relation_serializer)
    @api.marshal_with(user_relation_serializer)
    def put(self, id):
        """Edit User Relation"""
        item = load(UserRelation, id)
        item = update(item, api.payload)
        return item, 201

    @roles_accepted("admin")
    def delete(self, id):
        """Delete User Relation"""
        item = load(UserRelation, id)
        delete(item)
        return "", 204