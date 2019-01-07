import datetime
from flask import request, current_app
from flask_restplus import Namespace, Resource, fields, marshal_with, reqparse, abort
from database import User, user_datastore, db
from flask_security import auth_token_required, roles_accepted

api = Namespace("users", description="User related operations")

user_fields = {
    'id': fields.String,
    'username': fields.String,
    'email': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'created_at': fields.DateTime,
    'confirmed_at': fields.DateTime,
    'roles': fields.List(fields.String),
}

username_check_fields


@api.route('/')
@api.doc("Show all users to staff users.")
class UserResourceList(Resource):

    @roles_accepted('admin', 'member')
    @marshal_with(user_fields)
    def get(self):
        users = User.query.all()
        return users


@api.route("/preferences")
class UserPreferenceResource(Resource):

    def post(self):
        # Todo implement check on auth token and clean it when OK.
        return 204


@api.route('/')
class UsernameResource(Resource):

    def get(self):
