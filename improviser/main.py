import hashlib
import os
import structlog

from admin_views import (
    UserAdminView, RiffExerciseAdminView, RolesAdminView, RiffAdminView, BaseAdminView,
    UserPreferenceAdminView, InstrumentAdminView, RiffExerciseItemAdminView, BackingTrackAdminView
)

from flask import Flask, url_for, current_app
from flask_admin import Admin
from flask_admin import helpers as admin_helpers

from flask_cors import CORS
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_security import (Security, user_registered)

from database import (
    db, Tag, RiffTag, RiffExerciseTag, user_datastore, UserPreference, Instrument, RiffExerciseItem,
    BackingTrack
)
from database import User, Role, Riff, RiffExercise
from security import ExtendedRegisterForm, ExtendedJSONRegisterForm

from apis import api
from version import VERSION

logger = structlog.get_logger(__name__)

# Create app
app = Flask(__name__, static_url_path='/static')
# NOTE: the extra headers need to be available in the API gateway: that is handled by zappa_settings.json
CORS(app, resources='/*', allow_headers='*', origins='*',
     expose_headers='Authorization,Content-Type,Authentication-Token,Quick-Authentication-Token')
DATABASE_URI = os.getenv('DATABASE_URI', 'postgres://improviser:improviser@localhost/improviser')

app.config['DEBUG'] = False if not os.getenv("DEBUG") else True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') if os.getenv('SECRET_KEY') else 'super-secret'
admin = Admin(app, name='iMproviser', template_mode='bootstrap3')

app.config['VERSION'] = VERSION
app.config['FLASK_ADMIN_SWATCH'] = 'flatly'
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') if os.getenv('SECRET_KEY') else 'super-secret'
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha256'
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT') if os.getenv('SECURITY_PASSWORD_SALT') \
    else 'SALTSALTSALT'

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
app.config['SECURITY_CONFIRMABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_CHANGEABLE'] = True
app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = ['email', 'username']
app.config['SECURITY_POST_CONFIRM_VIEW'] = "https://www.improviser.education/login"
app.config['SECURITY_POST_RESET_VIEW'] = "https://www.improviser.education/login"
app.config["FRONTEND_URI"] = os.getenv("FRONTEND_URI") if os.getenv("FRONTEND_URI") else "localhost:5000"

# Needed for REST token login
# Todo: check if we can fix this without completely disabling it: it's only needed when login request is not via .json
app.config['WTF_CSRF_ENABLED'] = False


# Setup Flask-Security with extended user registration
security = Security(app, user_datastore, register_form=ExtendedRegisterForm,
                    confirm_register_form=ExtendedJSONRegisterForm)
login_manager = LoginManager(app)
mail = Mail()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


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


# ensure that new users are in an role
@user_registered.connect_via(app)
def on_user_registered(sender, user, confirm_token):
    user_datastore.add_role_to_user(user, "student")
    # set up user preferences default with sensible defaults
    default_instrument = Instrument.query.filter(Instrument.name == "Generic C").first()
    user_preference = UserPreference(instrument_id=default_instrument.id, user_id=user.id)
    try:
        db.session.add(user_preference)
        db.session.commit()
    except Exception as error:
        print(F"error while creating user prefs?: {error}")
        db.session.rollback()


@login_manager.request_loader
def load_user_from_request(request):
    # try to login using the quick token
    quick_token = request.headers.get("Quick-Authentication-Token")
    if quick_token:
        try:
            user_id, token = quick_token.split(":")
        except:
            return None

        quick_token_md5 = hashlib.md5(token.encode("utf-8")).hexdigest()
        user = User.query \
            .filter(User.id == user_id) \
            .filter(User.quick_token == quick_token_md5) \
            .first()
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# Views
api.init_app(app)
db.init_app(app)
mail.init_app(app)
admin.add_view(RiffAdminView(Riff, db.session))
admin.add_view(RiffExerciseAdminView(RiffExercise, db.session))
admin.add_view(RiffExerciseItemAdminView(RiffExerciseItem, db.session))
admin.add_view(BackingTrackAdminView(BackingTrack, db.session))
admin.add_view(UserAdminView(User, db.session))
admin.add_view(UserPreferenceAdminView(UserPreference, db.session))
admin.add_view(InstrumentAdminView(Instrument, db.session))
admin.add_view(RolesAdminView(Role, db.session))
admin.add_view(BaseAdminView(Tag, db.session))
admin.add_view(BaseAdminView(RiffTag, db.session))
admin.add_view(BaseAdminView(RiffExerciseTag, db.session))

migrate = Migrate(app, db)
logger.info("Ready loading admin views and api")

if __name__ == '__main__':
    app.run()
