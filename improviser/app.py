import datetime
import os
import uuid

from flask import Flask, abort, flash, request, url_for, Response
from flask_admin import helpers as admin_helpers
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask_cors import CORS
from flask_login import UserMixin, current_user
from flask_mail import Mail
from flask_migrate import Migrate, MigrateCommand
from flask_restplus import Api, Resource, fields, marshal_with, reqparse
from flask_script import Manager
from flask_security import RoleMixin, SQLAlchemyUserDatastore, Security, utils
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup
from sqlalchemy.dialects.postgresql.base import UUID
from wtforms import PasswordField


VERSION = '0.2.0'
DATABASE_URI = os.getenv('DATABASE_URI', 'postgres://improviser:improviser@localhost/improviser')

KEYS = ['c', 'cis', 'd', 'dis', 'ees', 'e', 'f', 'fis', 'g', 'gis', 'aes', 'a', 'ais', 'bes', 'b']
OCTAVES = [-1, 0, 1, 2]
app = Flask(__name__, static_url_path='/static')
CORS(app)
app.secret_key = 'TODO:MOVE_TO_BLUEPRINT'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
app.config['SECURITY_PASSWORD_SALT'] = 'SALTSALTSALT'

# Replace the next six lines with your own SMTP server settings
app.config['SECURITY_EMAIL_SENDER'] = os.getenv('SECURITY_EMAIL_SENDER') if os.getenv('SECURITY_EMAIL_SENDER') \
    else 'no-reply@example.com'
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER') if os.getenv('MAIL_SERVER') else 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME') if os.getenv('MAIL_USERNAME') else 'no-reply@example.com'
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') if os.getenv('MAIL_PASSWORD') else 'somepassword'

# More Flask Security settings
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_REGISTER_URL'] = '/admin/create_account'
app.config['SECURITY_LOGIN_URL'] = '/admin/login'
app.config['SECURITY_POST_LOGIN_VIEW'] = '/admin'
app.config['SECURITY_LOGOUT_URL'] = '/admin/logout'
app.config['SECURITY_POST_LOGOUT_VIEW'] = '/admin'
app.config['SECURITY_RESET_URL'] = '/admin/reset'
app.config['SECURITY_CHANGE_URL'] = '/admin/change'
app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = ['email', 'username']

# setup DB
db = SQLAlchemy(app)
db.UUID = UUID

api = Api(app)
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
admin = Admin(app, name='iMproviser', template_mode='bootstrap3')
mail = Mail(app)


@app.context_processor
def version():
    return dict(version=VERSION)


# Define models
class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.UUID(as_uuid=True), db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.UUID(as_uuid=True), db.ForeignKey('role.id'))


class Role(db.Model, RoleMixin):
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


class User(db.Model, UserMixin):
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary='roles_users',
                            backref=db.backref('users', lazy='dynamic'))

    # Human-readable values for the User when editing user related stuff.
    def __str__(self):
        return f'{self.username} : {self.email}'

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.email)


class Riff(db.Model):
    __tablename__ = 'riffs'
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = db.Column(db.String(255), unique=True, index=True)
    number_of_bars = db.Column(db.Integer())
    notes = db.Column(db.String(255))
    chord = db.Column(db.String(255), index=True)
    render_valid = db.Column(db.Boolean, default=False)
    render_date = db.Column(db.DateTime)
    image_info = db.Column(db.JSON)
    riff_exercises = db.relationship('RiffExercise', secondary='riff_exercise_items',
                                     backref=db.backref('riffs', lazy='dynamic'))
    def __repr__(self):
        return '<Riff %r>' % self.name


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


class RiffExercise(db.Model):
    __tablename__ = 'riff_exercises'
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = db.Column(db.String(255))
    is_global = db.Column(db.Boolean, default=True)
    created_by = db.Column('created_by', db.UUID(as_uuid=True), db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<RiffExercise %r>' % self.name


class RiffExerciseItem(db.Model):
    __tablename__ = 'riff_exercise_items'
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    riff_exercise_id = db.Column('riff_exercise_id', db.UUID(as_uuid=True), db.ForeignKey('riff_exercises.id'))
    riff_id = db.Column('riff_id', db.UUID(as_uuid=True), db.ForeignKey('riffs.id'))
    riff_root_key = db.Column(db.String(3), default='c')
    order_number = db.Column(db.Integer, primary_key=True, index=True)
    created_by = db.Column('created_by', db.UUID(as_uuid=True), db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )


# Executes before the first request is processed.
@app.before_first_request
def before_first_request():
    user_datastore.find_or_create_role(name='admin', description='God mode!')
    user_datastore.find_or_create_role(name='moderator', description='Can moderate other users content')
    user_datastore.find_or_create_role(name='operator', description='Can create and block users')

    # Create a default user
    encrypted_password = utils.hash_password('acidjunk@gmail.com')
    if not user_datastore.get_user('acidjunk@gmail.com'):
        user_datastore.create_user(email='acidjunk@gmail.com', password=encrypted_password)
        db.session.commit()
        user_datastore.add_role_to_user('acidjunk@gmail.com', 'admin')
        db.session.commit()


riff_serializer = api.model('Riff', {
    'name': fields.String(required=True, description='Unique riff name'),
    'number_of_bars': fields.Integer(required=True, description='Number of bars'),
    'notes': fields.String(required=True, description='Lilypond representation of the riff'),
    'chord': fields.String(description='Chord if known'),
})

riff_render_serializer = api.model('Riff', {
    'render_valid': fields.Boolean(required=True, description='Whether a render is deemed valid.'),
    'image_info': fields.String(description="The metainfo for all images for this riff, per key, octave")
})

riff_exercise_serializer = api.model('RiffExercise', {
    'name': fields.String(required=True, description='Unique exercise name'),
    'is_global': fields.Boolean(description="Is this riff exercise visible to everyone?", default=False),
})

# Todo: make this a nested list: so order can be dealt with easily
riff_exercise_item_serializer = api.model('RiffExerciseItem', {
    'riff_exercise_id': fields.String(required=True, description='Unique exercise name'),
    'riff_id': fields.Boolean(description="Is this riff exercise visible to everyone?"),
})

image_info_marshaller = parameter_marshaller = {
    "key_octave": fields.String,
    "width": fields.Integer,
    "height": fields.Integer,
    "staff_center": fields.Integer,
}

riff_fields = {
    'id': fields.String,
    'difficulty': fields.String,
    'name': fields.String,
    'number_of_bars': fields.Integer,
    'notes': fields.String,
    'chord': fields.String,
    'image': fields.String,
    'image_info': fields.Nested(image_info_marshaller),
    'render_valid': fields.Boolean,
    'render_date': fields.DateTime,
}

music_xml_info_marshaller = {
    "key_octave": fields.String,
    "music_xml": fields.String,
}

riff_detail_fields = {
    **riff_fields,
    'music_xml_info': fields.List(
        fields.Nested(music_xml_info_marshaller),
        description='Music XML representation of the riff in all available keys')
}

riff_exercise_fields = {
    'id': fields.String,
    'name': fields.String,
    # 'riffs': fields.List,
    'created_by': fields.String,  # or UUID of the user?
    'created_at': fields.DateTime,
}
riff_exercise_detail_fields = riff_exercise_fields
# Todo: investigate: e.g. use a deep_copy?
riff_exercise_detail_fields["riffs"] = fields.List(fields.Nested(riff_fields))

riff_arguments = reqparse.RequestParser()
riff_arguments.add_argument('search_phrase', type=str, required=False,
                            help='Return only items that contain the search_phrase')
riff_arguments.add_argument('show_unrendered', type=bool, required=False, default=False,
                            help='Toggle so you can see unrendered riffs also')

riff_exercise_arguments = reqparse.RequestParser()
riff_exercise_arguments.add_argument('search_phrase', type=str, required=False,
                                     help='Return only items that contain the search_phrase')


def convertToMusicXML(lilypond, tranpose='c'):
    import ly.musicxml
    e = ly.musicxml.writer()

    prefix = """\\transpose c %s {
    {
    \\version "2.12.3"
    \\clef treble
    \\time 4/4
    \override Staff.TimeSignature #'stencil = ##f
    """
    postfix = """}
    }
    \paper{
                indent=0\mm
                line-width=120\mm
                oddFooterMarkup=##f
                oddHeaderMarkup=##f
                bookTitleMarkup = ##f
                scoreTitleMarkup = ##f
            }"""

    xml_header = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">"""

    lilypond = f"{prefix % tranpose}\n{lilypond}\n{postfix}"
    e.parse_text(lilypond)
    # xml = bytes(xml_header, encoding='UTF-8') + e.musicxml().tostring()
    # return {xml}
    xml = xml_header + str(e.musicxml().tostring())
    return xml

@api.route('/riffs')
class RiffResourceList(Resource):

    @marshal_with(riff_fields)
    @api.expect(riff_arguments)
    def get(self):
        args = request.args
        # handle case insensitive search
        if args.get("search_phrase"):
            riffs_query = Riff.query.filter(Riff.name.ilike('%' + args["search_phrase"] + '%'))
        else:
            riffs_query = Riff.query

        # show all riffs or only rendered?
        show = "rendered"
        if args.get("show_unrendered") and args["show_unrendered"] == "true":
            show = "all"
        if "all" not in show:
            riffs_query = riffs_query.filter(Riff.render_valid)

        riffs = riffs_query.all()
        for riff in riffs:
            riff.image = f"https://www.improviser.education/static/rendered/120/riff_{riff.id}_c.png"
        return riffs

    @api.expect(riff_serializer)
    def post(self):
        riff = Riff(**api.payload)
        try:
            db.session.add(riff)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            abort(400, 'DB error: {}'.format(str(error)))
        return 201


@api.route('/riffs/<string:riff_id>')
class RiffResource(Resource):

    @marshal_with(riff_detail_fields)
    def get(self, riff_id):
        riff = Riff.query.filter_by(id=riff_id).first_or_404()
        riff.image = f"https://www.improviser.education/static/rendered/120/riff_{riff.id}_c.png"
        # todo: marshall dict -> key:music_xml
        result = []
        for octave in OCTAVES:
            result += [{"key_octave": key if not octave else f"{key}_{octave}",
                        "music_xml": convertToMusicXML(riff.notes, key)} for key in KEYS]
        riff.music_xml_info = result
        return riff

    @api.expect(riff_serializer)
    def put(self, riff_id):
        riff = Riff.query.filter_by(id=riff_id).first_or_404()
        # Todo implement real update
        return 204


@api.route('/riffs/rendered/<string:riff_id>')
class RiffResourceRendered(Resource):
    @api.expect(riff_render_serializer)
    def put(self, riff_id):
        riff = Riff.query.filter_by(id=riff_id).first_or_404()
        riff.render_valid = api.payload["render_valid"]
        riff.image_info = api.payload["image_info"]
        riff.render_date = datetime.datetime.now()
        db.session.commit()
        return 204


@api.route('/riff-exercises')
class RiffExerciseResourceList(Resource):

    @marshal_with(riff_exercise_fields)
    @api.expect(riff_exercise_arguments)
    def get(self):
        args = request.args
        # handle case insensitive search
        if args.get("search_phrase"):
            riff_exercises_query = RiffExercise.query.filter(RiffExercise.name.ilike('%' + args["search_phrase"] + '%'))
        else:
            riff_exercises_query = RiffExercise.query

        # todo: filter on created_by and is_global
        return riff_exercises_query.all()

    @api.expect(riff_exercise_serializer)
    def post(self):
        """A new riff is always just a name. Note Riff Items will be added via update..."""
        riff_exercise = RiffExercise(**api.payload)
        # Todo: add user
        try:
            db.session.add(riff_exercise)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            abort(400, 'DB error: {}'.format(str(error)))
        return 201


@api.route('/riff-exercises/<string:riff_exercise_id>')
class RiffExerciseResource(Resource):
    @api.expect(riff_exercise_serializer)
    def put(self, riff_exercise_id):
        riff_exercise = RiffExercise.query.filter_by(id=riff_exercise_id).first_or_404()
        riff_exercise.name = api.payload["name"]
        riff_exercise.is_global = api.payload["name"]
        # Todo: add items also.

        db.session.commit()
        return 204

    @marshal_with(riff_exercise_fields)
    def get(self, riff_exercise_id):
        riff_exercise = RiffExercise.query.filter_by(id=riff_exercise_id).first_or_404()
        # Todo: do stuff with items also.
        return riff_exercise



@app.route('/test-musicxml')
def testMusicXMLALL():
    riffs = Riff.query.all()
    ly_string = ""
    for riff in riffs:
        if riff.render_valid:
            bar_separator = '\\bar "|"'
            ly_string = f' {ly_string} {riff.notes} {bar_separator}'
    # strip first space and bar suffix
    ly_string = ly_string[1:-5]
    # Todo: we desperately need logging
    print(f"Ly string: before return=> {ly_string}")
    return Response(response=convertToMusicXML(ly_string), status=200, mimetype="application/xml")


class UserAdminView(ModelView):
    # Don't display the password on the list of Users
    column_exclude_list = list = ('password',)

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True
    can_set_page_size = True

    # Prevent administration of Users unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        if 'admin' in current_user.roles:
            return True

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):
        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdminView, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):
        # If the password field isn't blank...
        if len(model.password2):
            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = utils.hash_password(model.password2)


class RolesAdminView(ModelView):

    # Prevent administration of Roles unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        if 'admin' in current_user.roles:
            return True


class RiffAdminView(ModelView):
    Riff.image = db.String
    column_list = ['id', 'name', 'render_valid', 'difficulty', 'notes', 'number_of_bars', 'chord', 'image']
    column_default_sort = ('name', True)
    column_filters = ('render_valid', 'number_of_bars', 'chord')
    column_searchable_list = ('id', 'name', 'chord', 'notes', 'number_of_bars')
    can_set_page_size = True

    def is_accessible(self):
        if 'admin' in current_user.roles:
            return True

    @action('render', 'Render', 'Are you sure you want to re-render selected riffs?')
    def action_approve(self, ids):
        try:
            query = Riff.query.filter(Riff.id.in_(ids))
            count = 0
            for riff in query.all():
                riff.render_valid = False
                flash('{} render of riffs successfully rescheduled.'.format(count))
        except Exception as error:
            if not self.handle_view_exception(error):
                flash('Failed to schedule re-render riff. {error}'.format(error=str(error)))

    def _list_thumbnail(view, context, model, name):
        return Markup(f'<img src="https://www.improviser.education/static/rendered/80/riff_{model.id}_c.png">')

    column_formatters = {
        'image': _list_thumbnail
    }


class RiffExerciseAdminView(ModelView):
    column_list = ['id', 'name', 'is_global', 'created_by', 'created_at']
    column_default_sort = ('name', True)
    column_searchable_list = ('id', 'name', 'created_by')
    can_set_page_size = True

    def is_accessible(self):
        if 'admin' in current_user.roles:
            return True


admin.add_view(RiffAdminView(Riff, db.session))
admin.add_view(RiffExerciseAdminView(RiffExercise, db.session))
admin.add_view(UserAdminView(User, db.session))
admin.add_view(RolesAdminView(Role, db.session))

if __name__ == '__main__':
    manager.run()
