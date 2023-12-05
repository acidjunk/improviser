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
from database import School, RolesUsers, UserRelation
from flask_restx import Namespace, Resource, abort, fields, marshal_with
from flask_security import roles_accepted
from flask_login import current_user

api = Namespace("schools", description="School related operations")

school_serializer = api.model(
    "School",
    {
        "id": fields.String(),
        "name": fields.String(required=True, description="Name of the School")
    },
)

parser = api.parser()
parser.add_argument("range", location="args", help="Pagination: default=[0,19]")
parser.add_argument("sort", location="args", help='Sort: default=["name","ASC"]')
parser.add_argument("filter", location="args", help="Filter default=[]")


@api.route("/")
@api.doc("Create schools")
class SchoolsResourceList(Resource):
    @marshal_with(school_serializer)
    @api.doc(parser=parser)
    def get(self):
        """List Schools"""
        args = parser.parse_args()
        range = get_range_from_args(args)
        sort = get_sort_from_args(args, "id")
        filter = get_filter_from_args(args)

        query_result, content_range = query_with_filters(School, School.query, range, sort, filter)
        return query_result, 200, {"Content-Range": content_range}

    @roles_accepted("admin", "student")
    @api.expect(school_serializer)
    @api.marshal_with(school_serializer)
    def post(self):
        school = School(id=str(uuid.uuid4()), name=api.payload["name"], created_by=current_user.id)
        relation = UserRelation(id=str(uuid.uuid4()), school_id=school.id, owner_id=current_user.id, created_by=current_user.id)
        owner_role = RolesUsers(user_id=current_user.id, role_id='4ad72d68-357e-42c5-b58b-b77349114376')

        save(school)
        save(relation)
        save(owner_role)
        return school, 201


@api.route("/<id>")
@api.doc("School detail operations.")
class SchoolsResource(Resource):
    @roles_accepted("admin", "school", "teacher")
    @marshal_with(school_serializer)
    def get(self, id):
        """List School"""
        item = load(School, id)
        return item, 200

    @roles_accepted("admin", "school")
    @api.expect(school_serializer)
    @api.marshal_with(school_serializer)
    def put(self, id):
        """Edit School"""
        item = load(School, id)
        item = update(item, api.payload)
        return item, 201

    @roles_accepted("admin", "school")
    def delete(self, id):
        """Delete School"""
        item = load(School, id)
        delete(item)
        return "", 204
