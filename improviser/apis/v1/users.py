import datetime
from database import db_session
from flask import request
from flask_restplus import Namespace, Resource, fields, marshal_with, reqparse, abort
from models import User


api = Namespace("users", description="User related operations")

login_serializer = api.model("User", {
    "email": fields.String(required=True, description="A verified e-mail address"),
    "password": fields.Integer(required=True, description="Password")
})

@api.route("/login")
class UserLoginResource(Resource):

    @api.expect(login_serializer)
    def post(self, riff_id):
        # Todo implement real update
        return 204


@api.route("/logout")
class UserLogoutResource(Resource):

    def post(self, riff_id):
        # Todo implement check on auth token and clean it when OK.
        return 204


@api.route("/register")
class RegisterUserResource(Resource):

    def post(self, riff_id):
        # Todo implement check on auth token and clean it when OK.
        return 204