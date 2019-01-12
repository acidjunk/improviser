import copy

from datetime import datetime
import hashlib
import uuid

from flask_restplus import Namespace, Resource, fields, marshal_with
from database import User
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
    'mail_offers': fields.Boolean,
    'mail_announcements': fields.Boolean,
}
quick_auth_fields = {
    'quick_token': fields.String,
    'quick_token_created_at': fields.DateTime,
}

user_message_fields = {
   'available': fields.Boolean,
   'reason': fields.String,
}


@api.route('/')
@api.doc("Show all users to staff users.")
class UserResourceList(Resource):

    @auth_token_required
    @roles_accepted('admin', 'member')
    @marshal_with(user_fields)
    def get(self):
        users = User.query.all()
        return users


@api.route('/current-user/<string:user_id>')
@api.doc("Retrieve info about currently logged in users and handle the quick-token session of users.")
class UserResource(Resource):

    @auth_token_required
    @marshal_with({**user_fields, **quick_auth_fields})
    def get(self, user_id):
        # todo add check or decorator for current user
        user = User.query.filter(User.id == user_id).first()
        quick_token = str(uuid.uuid4())
        quick_token_md5 = hashlib.md5(quick_token.encode('utf-8')).hexdigest()
        user.quick_token = quick_token_md5
        print(f"md5: {quick_token_md5}, normal: {quick_token}")
        user.quick_token_created_at = datetime.now()

        # get the response ready, without overwriting the DB
        shallow_user = copy.copy(user)
        shallow_user.quick_token = quick_token
        return shallow_user


@api.route('/validate-username/<string:username>')
class ValidateUsernameResource(Resource):

    def get(self, username):
        user = User.query.filter(User.username == username).first()
        if not user:
            return {'available': True, 'reason': ''}
        else:
            return {'available': False, 'reason': 'Username already taken'}


@api.route('/validate-email/<string:email>')
class ValidateEmailResource(Resource):

    def get(self, email):
        user = User.query.filter(User.email == email).first()
        if not user:
            return {'available': True, 'reason': ''}
        else:
            return {'available': False, 'reason': 'Email already exists'}
