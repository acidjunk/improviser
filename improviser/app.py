import datetime
import uuid

import os
import sys
from flask import Flask, flash, request, url_for
from flask_admin import helpers as admin_helpers
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask_login import UserMixin, current_user
from flask_mail import Mail
from flask_migrate import Migrate, MigrateCommand
from flask_restplus import Api, Resource, fields, marshal_with
from flask_script import Manager
from flask_security import RoleMixin, SQLAlchemyUserDatastore, Security, utils
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup
from sqlalchemy.dialects.postgresql.base import UUID
from wtforms import PasswordField

sys.path.append('../')
from improviser.render.render import Render  # noqa

VERSION = '0.1.2'

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'TODO:MOVE_TO_BLUEPRINT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://improviser:improviser@localhost/improviser'
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
renderer = Render(renderPath=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'rendered'))
mail = Mail(app)


@app.context_processor
def version():
    return dict(version=VERSION)


riff_fields = {
    'id': fields.String,
    'difficulty': fields.String,
    'name': fields.String,
    'number_of_bars': fields.Integer,
    'notes': fields.String,
    'chord': fields.String,
    'image': fields.String,
    'render_valid': fields.Boolean,
    'render_date': fields.DateTime,
}


def render(riff):
    keys = ['c', 'f', 'g']  # only c,f,g for now

    for key in keys:
        renderer.name = "riff_%s_%s" % (riff.id, key)
        notes = riff.notes.split(" ")
        renderer.addNotes(notes)
        renderer.set_cleff('treble')
        renderer.doTranspose(key)
        if not renderer.render():
            print(f"Error: couldn't render riff.id: {riff.id}")


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

    def __repr__(self):
        return '<Riff %r>' % self.name


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


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

@api.route('/api/riffs')
class RiffListResource(Resource):

    @marshal_with(riff_fields)
    def get(self):
        args = request.args
        if args:
            riffs = Riff.query.filter(Riff.name.contains(args["search_phrase"])).all()
        else:
            riffs = Riff.query.all()
        for riff in riffs:
            riff.image = url_for("static", filename=f"rendered/large/riff_{riff.id}_c.png")
        return riffs


@api.route('/api/populate')
class PopulateAppResource(Resource):

    def get(self):
        #Todo: fix chord + difficulty


        # Some fun stuff popular
        lily = []

        lily.append(("fis''4 e''8 b'4 g' fis''8~ fis''4 e''8 b'4 g' r8", "medium", 1, "Careless whisper 1"))
        lily.append(("d''4 c''8 g'4 e' d''8~ d''4 c''8 g'4 e' r8", "medium", 1, "Careless whisper 2"))
        lily.append(("c''4 b'8 g'4 e'4 c'8~ c'1", "medium", 1, "Careless whisper 3"))
        lily.append(("b4 c' d' e' fis' g' a' b'", "medium", 1, "Careless whisper 4"))

        # minor riffs only
        lily.append(("bes'8. bes'16 r4 bes'8. bes'16 r4 r8 bes'8 c''16 bes'8 es''16 r2", "medium", 2, "Funk 1"))
        lily.append(("r4 es''16 d''8 c''16 c''8 bes'8 r4 bes'8 r16 bes'16 r4 r8 c''16 r16 r4", "medium", 2, "Funk 2"))

        # easy
        lily.append(("c' d' e' f' g' a' b' c'' d'' e'' f'' g'' a'' b'' c'''2", "easy", 2, "plain scale easy"))
        lily.append(("c' d' e' g' a' c'' d'' e'' g'' a'' c'''2", "easy", 2, "pentatonic scale easy"))
        lily.append(("c' d' e' fis' g' a' b' c'' d'' e'' fis'' g'' a'' b'' c'''2", "easy", 2, "lydian easy"))
        lily.append(("c' d' e' f' g' a' bes' c'' d'' e'' f'' g'' a'' bes'' c'''2", "easy", 2, "mixolydian easy"))
        lily.append(("c'4 d' ees' e' f' g' a' c'' d'' ees'' e'' f'' g'' a''4 c'''2", "easy", 2, "major blues scale"))

        lily.append(("c' d' ees' f' g' aes' b' c'' c'' d'' ees'' f'' g'' ges'' b'' c'''", "easy", 2,
                     "natural harmonic minor easy"))
        lily.append(("c' d' ees' f' g' a' b' c'' c'' d'' ees'' f'' g'' a'' b'' c'''", "easy", 2,
                     "natural melodic minor easy"))  # TODO: implement some smart stuff get a correct reversed scale
        lily.append(("c' d' ees' f' g' a' bes' c'' c'' d'' ees'' f'' g'' a'' bes'' c'''", "easy", 2, "dorian easy"))
        lily.append(("c' des' ees' f' g' a' bes' c''", "easy", 2, "phrygian easy"))

        lily.append(("c' ees' g' ees' g' c'' g' c'' ees'' c'' ees'' g'' ees'' g'' c'''2", "easy", 4,
                     "minor broken chord easy"))
        lily.append(("c'4 ees' f' fis' g' bes' c''2 c''4 ees'' f'' fis'' g'' bes''4 c'''2", "medium", 2,
                     "minor blues scale easy"))

        # medium
        lily.append(("c'4 d'8 ees' f' g' aes' bes' c''4 d''8 ees'' f'' g'' aes'' bes''8", "medium", 2,
                     "minor plain scale medium"))
        lily.append(("c'8 ees' g' ees' g' c'' g' c'' ees'' c'' ees'' g'' ees'' g''8 c'''4", "medium", 2,
                     "minor broken chord medium"))
        lily.append(("c'4 ees'8 f' fis' g' bes'4 c''4 ees''8 f'' fis'' g''8 bes''4", "medium", 2,
                     "minor blues scale medium"))

        # hard
        lily.append(("c'8 f' bes' ees'' c'' f'' a'' g'' ees'' des'' aes' ges' b' a' e' d'8", "hard", 2,
                     "fourths in key in & out hard"))
        lily.append(("f' c' f' g' aes' ees' aes' bes' b' e'' cis'' fis'' b'' e''' cis''' a'' gis'' cis''' ais'' dis''' "
                     "c'' g'' f'' bes'' a'' e'' a'' g'' d'' a' g' c''", "hard", 4, "fourths in key in & out hard"))
        lily.append(("c'8 f' bes' g' c'' f'' d'' g'' c''' d''' a'' e'' d'' g'' f'' c''8", "hard", 2,
                     "fourths in key hard"))

        for li in lily:
            riff = Riff(name=li[3], number_of_bars=li[2], notes=li[0], chord=li[1])
            try:
                db.session.add(riff)
                db.session.commit()
                print(f"Added {riff.name}")
            except Exception as error:
                db.session.rollback()
                print(f"Skipped {riff.name} with {error}")


@api.route('/api/render/all')
class RenderRiff(Resource):

    def get(self):
        riffs = Riff.query.all()
        for riff in riffs:
            render(riff)

            # internal bookkeeping
            riff.render_date = datetime.datetime.now()
            riff.render_valid = True
            db.session.commit()


class UserAdminView(ModelView):
    # Don't display the password on the list of Users
    column_exclude_list = list = ('password',)

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True

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
    column_list = ['id', 'name', 'difficulty', 'notes', 'number_of_bars', 'chord', 'image']
    column_default_sort = ('name', True)
    column_filters = ('number_of_bars', 'chord')
    column_searchable_list = ('name', 'chord')

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

                # todo, move rendering to background thread, for now eagerly render it:
                render(riff)
        except Exception as error:
            if not self.handle_view_exception(error):
                flash('Failed to re-render riff. {error}'.format(error=str(error)))

    def _list_thumbnail(view, context, model, name):
        return Markup('<img src="%s">' % url_for('static', filename=f'rendered/small/riff_{model.id}_c.png'))

    column_formatters = {
        'image': _list_thumbnail
    }


admin.add_view(RiffAdminView(Riff, db.session))
admin.add_view(UserAdminView(User, db.session))
admin.add_view(RolesAdminView(Role, db.session))

if __name__ == '__main__':
    manager.run()
