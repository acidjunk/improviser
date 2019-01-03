import datetime
from flask import request, current_app
from flask_restplus import Namespace, Resource, fields, marshal_with, reqparse, abort
from database import User, user_datastore, db
from flask_security import login_user

api = Namespace("users", description="User related operations")

login_serializer = api.model("UserLogin", {
    "email": fields.String(required=True, description="A verified e-mail address"),
    "password": fields.String(required=True, description="Password"),
})
new_user_serializer = api.model("UserProfile", {
    "username": fields.String(required=True, description="Username"),
    "email": fields.String(required=True, description="E-mail address"),
    "first_name": fields.String(required=True, description="First name"),
    "last_name": fields.String(required=True, description="Last name"),
})


@api.route("/login")
class UserLoginResource(Resource):

    @api.expect(login_serializer)
    @marshal_with({"authentication_token": fields.String})
    def post(self):
        # Todo implement real update
        user = User.query.filter_by(email='acidjunk@gmail.com').first()
        token = user.get_auth_token()
        return {"authentication_token": token}


@api.route("/logout")
class UserLogoutResource(Resource):

    def post(self, user):
        # Todo implement check on auth token and clean it when OK.
        return 204


@api.route("/preferences")
class UsePreferenceResource(Resource):

    def post(self):
        # Todo implement check on auth token and clean it when OK.
        return 204


@api.route("/register")
class RegisterUserResource(Resource):

    @api.expect(new_user_serializer)
    def post(self):
        try:
            user_datastore.create_user(
                email=api.payload["email"],
                username=api.payload["username"],
                password='banaan',
                first_name=api.payload["first_name"],
                last_name=api.payload["last_name"],
            )
            # Todo implement check on auth token and clean it when OK.
            db.session.commit()
        except:
            db.session.rollback()
            abort(409)
        return 204
