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


@api.route('/<string:user_id>')
class UserResource(Resource):

    @auth_token_required
    @marshal_with(user_fields)
    def get(self, user_id):
        # todo add check or decorator for current user
        user = User.query.filter(User.id == user_id).first()
        return user


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
