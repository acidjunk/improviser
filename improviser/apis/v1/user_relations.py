import requests
import uuid
import os

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

user_model_fields = {
    "id": fields.String(),
    "first_name": fields.String(),
    "last_name": fields.String()
}

school_model_fields = {
    "id": fields.String(),
    "name": fields.String()
}

user_relation_serializer_with_users = api.model(
    "User Relation with Users",
    {
        "id": fields.String(),
        "school": fields.Nested(school_model_fields),
        "owner": fields.Nested(user_model_fields),
        "teacher": fields.Nested(user_model_fields),
        "student": fields.Nested(user_model_fields),
    },
)

parser = api.parser()
parser.add_argument("range", location="args", help="Pagination: default=[0,19]")
parser.add_argument("sort", location="args", help='Sort: default=["name","ASC"]')
parser.add_argument("filter", location="args", help="Filter default=[]")


@api.route("/")
@api.doc("Create user relations")
class UserRelationsResourceList(Resource):
    @marshal_with(user_relation_serializer_with_users)
    @api.doc(parser=parser)
    def get(self):
        """List User Relations"""
        args = parser.parse_args()
        range = get_range_from_args(args)
        sort = get_sort_from_args(args, "id")
        filter = get_filter_from_args(args)

        query_result, content_range = query_with_filters(UserRelation, UserRelation.query, range, sort, filter)

        serialized_result = []
        for relation in query_result:
            serialized_relation = {
                "id": relation.id,
                "school": {
                    "id": relation.school.id,
                    "name": relation.school.name,
                },
                "owner": {
                    "id": relation.owner.id,
                    "first_name": relation.owner.first_name,
                    "last_name": relation.owner.last_name,
                },
            }

            if relation.teacher:
                serialized_relation["teacher"] = {
                    "id": relation.teacher.id,
                    "first_name": relation.teacher.first_name,
                    "last_name": relation.teacher.last_name,
                }

            if relation.student:
                serialized_relation["student"] = {
                    "id": relation.student.id,
                    "first_name": relation.student.first_name,
                    "last_name": relation.student.last_name,
                }

            serialized_result.append(serialized_relation)

        return serialized_result, 200, {"Content-Range": content_range}

    @roles_accepted("admin", "school", "teacher")
    @api.expect(user_relation_serializer)
    @api.marshal_with(user_relation_serializer)
    def post(self):
        owner = User.query.filter(User.id == api.payload["owner_id"]).first()

        baseurl = os.environ.get('API_URL') + os.environ.get('API_VERSION')
        headers = {'Content-Type': 'application/json'}
        r = requests.get(baseurl + '/licenses/improviser/' + str(api.payload["owner_id"]), headers=headers)
        license = r.json()

        person_count = 0
        relations = UserRelation.query.filter(UserRelation.owner_id == api.payload["owner_id"])

        for relation in relations:
            if relation.teacher or relation.student:
                person_count += 1

        if person_count >= license['seats']:
            abort(400, "Seat limit reached for this School")

        if not owner:
            abort(400, "Owner not found")

        teacher_id = api.payload.get('teacher_id')
        student_id = api.payload.get('student_id')
        if student_id:
            student = User.query.filter(User.id == student_id).first()
            teacher = User.query.filter(User.id == teacher_id).first()

            if not student or not teacher:
                abort(400, "Student or teacher not found")

        elif teacher_id:
            teacher = User.query.filter(User.id == teacher_id).first()

            if not teacher:
                abort(400, "Teacher not found")

        relation = UserRelation(id=str(uuid.uuid4()), **api.payload)

        save(relation)
        return relation, 201


@api.route("/<id>")
@api.doc("User Relation detail operations.")
class UserRelationsResource(Resource):
    @roles_accepted("admin", "school", "teacher")
    @marshal_with(user_relation_serializer_with_users)
    def get(self, id):
        """List User Relation"""
        item = load(UserRelation, id)

        serialized_relation = {
            "id": item.id,
            "school": {
                "id": item.school.id,
                "name": item.school.name,
            },
            "owner": {
                "id": item.owner.id,
                "first_name": item.owner.first_name,
                "last_name": item.owner.last_name,
            },
        }

        if item.teacher:
            serialized_relation["teacher"] = {
                "id": item.teacher.id,
                "first_name": item.teacher.first_name,
                "last_name": item.teacher.last_name,
            }

        if item.student:
            serialized_relation["student"] = {
                "id": item.student.id,
                "first_name": item.student.first_name,
                "last_name": item.student.last_name,
            }

        return serialized_relation, 200


@api.route("/teacher/<id>")
@api.doc("User Relation detail operations.")
class UserRelationsResource(Resource):
    @roles_accepted("admin", "school")
    @api.expect(user_relation_serializer)
    @api.marshal_with(user_relation_serializer)
    def delete(self, id):
        """Edit User Relation"""
        all_items = UserRelation.query.all()

        payload = {
            "teacher_id": None
        }

        for item in all_items:
            if str(item.teacher_id) == id:
                update(item, payload)

        return "", 204


@api.route("/student/<id>")
@api.doc("User Relation detail operations.")
class UserRelationsResource(Resource):

    @roles_accepted("admin", "school", "teacher")
    def delete(self, id):
        """Delete User Relation"""
        item = load(UserRelation, id)
        delete(item)
        return "", 204


@api.route("/owner/<owner_id>")
@api.doc("User Relation detail operations.")
class UserRelationsResource(Resource):
    @roles_accepted("admin", "school")
    @marshal_with(user_relation_serializer_with_users)
    def get(self, owner_id):
        """List User Relation"""
        args = parser.parse_args()
        range = get_range_from_args(args)
        sort = get_sort_from_args(args, "id")
        filter = get_filter_from_args(args)

        query_result, content_range = query_with_filters(UserRelation, UserRelation.query, range, sort, filter)

        serialized_result = []
        for relation in query_result:
            if str(relation.owner_id) == str(owner_id):
                serialized_relation = {
                    "id": relation.id,
                    "school": {
                        "id": relation.school.id,
                        "name": relation.school.name,
                    },
                    "owner": {
                        "id": relation.owner.id,
                        "first_name": relation.owner.first_name,
                        "last_name": relation.owner.last_name,
                    },
                }

                if relation.teacher:
                    serialized_relation["teacher"] = {
                        "id": relation.teacher.id,
                        "first_name": relation.teacher.first_name,
                        "last_name": relation.teacher.last_name,
                    }

                if relation.student:
                    serialized_relation["student"] = {
                        "id": relation.student.id,
                        "first_name": relation.student.first_name,
                        "last_name": relation.student.last_name,
                    }

                serialized_result.append(serialized_relation)

        return serialized_result, 200, {"Content-Range": content_range}


@api.route("/teacher/<teacher_id>")
@api.doc("User Relation detail operations.")
class UserRelationsResource(Resource):
    @roles_accepted("admin", "school", "teacher")
    @marshal_with(user_relation_serializer_with_users)
    def get(self, teacher_id):
        """List User Relation"""
        args = parser.parse_args()
        range = get_range_from_args(args)
        sort = get_sort_from_args(args, "id")
        filter = get_filter_from_args(args)

        query_result, content_range = query_with_filters(UserRelation, UserRelation.query, range, sort, filter)

        serialized_result = []
        for relation in query_result:
            if str(relation.teacher_id) == str(teacher_id):
                serialized_relation = {
                    "id": relation.id,
                    "school": {
                        "id": relation.school.id,
                        "name": relation.school.name,
                    },
                    "owner": {
                        "id": relation.owner.id,
                        "first_name": relation.owner.first_name,
                        "last_name": relation.owner.last_name,
                    },
                }

                if relation.teacher:
                    serialized_relation["teacher"] = {
                        "id": relation.teacher.id,
                        "first_name": relation.teacher.first_name,
                        "last_name": relation.teacher.last_name,
                    }

                if relation.student:
                    serialized_relation["student"] = {
                        "id": relation.student.id,
                        "first_name": relation.student.first_name,
                        "last_name": relation.student.last_name,
                    }

                serialized_result.append(serialized_relation)

        return serialized_result, 200, {"Content-Range": content_range}


@api.route("/school/<school_id>")
@api.doc("User Relation detail operations.")
class UserRelationsResource(Resource):
    @roles_accepted("admin", "school", "teacher")
    @marshal_with(user_relation_serializer_with_users)
    def get(self, school_id):
        """List User Relation"""
        args = parser.parse_args()
        range = get_range_from_args(args)
        sort = get_sort_from_args(args, "id")
        filter = get_filter_from_args(args)

        query_result, content_range = query_with_filters(UserRelation, UserRelation.query, range, sort, filter)

        serialized_result = []
        for relation in query_result:
            if str(relation.school_id) == str(school_id):
                serialized_relation = {
                    "id": relation.id,
                    "school": {
                        "id": relation.school.id,
                        "name": relation.school.name,
                    },
                    "owner": {
                        "id": relation.owner.id,
                        "first_name": relation.owner.first_name,
                        "last_name": relation.owner.last_name,
                    },
                }

                if relation.teacher:
                    serialized_relation["teacher"] = {
                        "id": relation.teacher.id,
                        "first_name": relation.teacher.first_name,
                        "last_name": relation.teacher.last_name,
                    }

                if relation.student:
                    serialized_relation["student"] = {
                        "id": relation.student.id,
                        "first_name": relation.student.first_name,
                        "last_name": relation.student.last_name,
                    }

                serialized_result.append(serialized_relation)

        return serialized_result, 200, {"Content-Range": content_range}