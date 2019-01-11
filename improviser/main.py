import os
import structlog

from admin_views import (UserAdminView, RiffExerciseAdminView, RolesAdminView, RiffAdminView, BaseAdminView)

from flask import Flask, url_for
from flask_admin import Admin
from flask_admin import helpers as admin_helpers

from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate
from flask_security import (Security, SQLAlchemySessionUserDatastore, LoginForm, login_user, user_registered)

from apis import api

from database import db, Tag, RiffTag, RiffExerciseTag, user_datastore
from database import User, Role, Riff, RiffExercise
from security import ExtendedRegisterForm, ExtendedJSONRegisterForm

logger = structlog.get_logger(__name__)

# Create app
app = Flask(__name__, static_url_path='/static')
CORS(app)
DATABASE_URI = os.getenv('DATABASE_URI', 'postgres://improviser:improviser@localhost/improviser')

app.config['DEBUG'] = False if not os.getenv("DEBUG") else True
app.config['SECRET_KEY'] = 'super-secret'
admin = Admin(app, name='iMproviser', template_mode='bootstrap3')

app.config['FLASK_ADMIN_SWATCH'] = 'flatly'
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
app.secret_key = 'TODO:MOVE_TO_BLUEPRINT'
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
app.config['SECURITY_PASSWORD_SALT'] = 'SALTSALTSALT'
# override the flask-security config for fast password hashes


# TODO: before deploy
app.config['SECURITY_HASHING_SCHEMES'] = ['plaintext']
app.config['SECURITY_DEPRECATED_HASHING_SCHEMES'] = []
app.config['SECURITY_PASSWORD_HASH'] = 'plaintext'



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
app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = ['email', 'username']

# Needed for REST token login
# Todo: check if we can fix this without completely disabling it: it's only needed when login request is not via .json
app.config['WTF_CSRF_ENABLED'] = False

# Setup Flask-Security with extended user registration
security = Security(app, user_datastore, register_form=ExtendedRegisterForm,
                    confirm_register_form=ExtendedJSONRegisterForm)
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


# Views
api.init_app(app)
db.init_app(app)
mail.init_app(app)

admin.add_view(RiffAdminView(Riff, db.session))
admin.add_view(RiffExerciseAdminView(RiffExercise, db.session))
admin.add_view(UserAdminView(User, db.session))
admin.add_view(RolesAdminView(Role, db.session))
admin.add_view(BaseAdminView(Tag, db.session))
admin.add_view(BaseAdminView(RiffTag, db.session))
admin.add_view(BaseAdminView(RiffExerciseTag, db.session))

migrate = Migrate(app, db)
logger.info("Ready loading admin views and api")


if __name__ == '__main__':
    app.run()
