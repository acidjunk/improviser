import copy

from datetime import datetime
import hashlib
import uuid
from flask_login import current_user

from flask_restplus import Namespace, Resource, fields, marshal_with, abort
from database import User, Instrument, UserPreference, db
from flask_security import auth_token_required, roles_accepted
from security import quick_token_required

api = Namespace("users", description="User related operations")

user_preference_fields = {
    'instrument_id': fields.String,
    'instrument_name': fields.String,
    'recent_exercises': fields.String,
    'recent_lessons': fields.String,
    'language': fields.String,
    'ideabook': fields.String,
}

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
    'preferences': fields.Nested(user_preference_fields)
}
quick_auth_fields = {
    'quick_token': fields.String,
    'quick_token_created_at': fields.DateTime,
}

user_message_fields = {
   'available': fields.Boolean,
   'reason': fields.String,
}

instrument_fields = {
    'id': fields.String,
    'name': fields.String,
    'root_key': fields.String
}

user_preference_serializer = api.model("UserPreference", {
    "instrument_id": fields.String(description="Id of users instrument"),
    "recent_exercises": fields.String(description="JSON list of recently used exercises"),
    "recent_lessons": fields.String(description="JSON list of recently used lessons"),
    "language": fields.String(description="Preferred language"),
    "ideabook": fields.String(description="Ideabook contents"),
})

@api.route('/')
@api.doc("Show all users to staff users.")
class UserResourceList(Resource):

    @auth_token_required
    @roles_accepted('admin', 'operator')
    @marshal_with(user_fields)
    def get(self):
        users = User.query.all()
        return users


@api.route('/current-user')
@api.doc("Retrieve info about currently logged in users and handle the quick-token session of users.")
class UserResource(Resource):

    @auth_token_required
    @marshal_with({**user_fields, **quick_auth_fields})
    def get(self):
        user = User.query.filter(User.id == current_user.id).first()
        quick_token = str(uuid.uuid4())
        quick_token_md5 = hashlib.md5(quick_token.encode('utf-8')).hexdigest()
        user.quick_token = quick_token_md5
        print(f"md5: {quick_token_md5}, normal: {quick_token}")
        user.quick_token_created_at = datetime.now()

        # get the response ready, without overwriting the DB
        shallow_user = copy.copy(user)
        shallow_user.quick_token = quick_token
        shallow_user.preferences.instrument_name = user.preferences.instrument.name
        return shallow_user


@api.route('/preferences')
class UserPreferenceResource(Resource):

    @quick_token_required
    @marshal_with(user_preference_fields)
    def get(self):
        user_preference = UserPreference.query.filter(UserPreference.user_id == current_user.id).first()
        user_preference.instrument_name = user_preference.instrument.name
        return user_preference

    @quick_token_required
    @api.expect(user_preference_serializer)
    def patch(self):
        user_preference = UserPreference.query.filter(UserPreference.user_id == current_user.id).first()
        if api.payload.get("language"):
            user_preference.language = api.payload["language"]
        if api.payload.get("instrument_id"):
            user_preference.instrument_id = api.payload["instrument_id"]
        if api.payload.get("recent_exercises"):
            user_preference.recent_exercises = api.payload["recent_exercises"]
        if api.payload.get("recent_lessons"):
            user_preference.recent_lessons = api.payload["recent_lessons"]
        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            abort(400, 'DB error: {}'.format(str(error)))
        return 204


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


@api.route('/instruments')
@api.doc("Show all instruments to users.")
class InstrumentResourceList(Resource):

    @quick_token_required
    @roles_accepted('admin', 'student')
    @marshal_with(instrument_fields)
    def get(self):
        return Instrument.query.all()
