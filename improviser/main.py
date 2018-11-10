import os
import structlog

from admin_views import UserAdminView, RiffExerciseAdminView, RolesAdminView, RiffAdminView

from flask import Flask, url_for
from flask_admin import Admin
from flask_admin import helpers as admin_helpers

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import (Security, SQLAlchemySessionUserDatastore)

from database import db_session
from models import User, Role, RiffExercise, Riff

from apis import api
logger = structlog.get_logger(__name__)

# Create app
app = Flask(__name__, static_url_path='/static')
CORS(app)
DATABASE_URI = os.getenv('DATABASE_URI', 'postgres://improviser:improviser@localhost/improviser')

# Todo: move config to other class??
app.config['DEBUG'] = False if not os.getenv("DEBUG") else True
app.config['SECRET_KEY'] = 'super-secret'
admin = Admin(app, name='iMproviser', template_mode='bootstrap3')

app.config['FLASK_ADMIN_SWATCH'] = 'flatly'
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
app.secret_key = 'TODO:MOVE_TO_BLUEPRINT'
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
app.config['SECURITY_PASSWORD_SALT'] = 'SALTSALTSALT'
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
app.config['SECURITY_REGISTER_URL'] = '/admin/create_account'
app.config['SECURITY_LOGIN_URL'] = '/admin/login'
app.config['SECURITY_POST_LOGIN_VIEW'] = '/admin'
app.config['SECURITY_LOGOUT_URL'] = '/admin/logout'
app.config['SECURITY_POST_LOGOUT_VIEW'] = '/admin'
app.config['SECURITY_RESET_URL'] = '/admin/reset'
app.config['SECURITY_CHANGE_URL'] = '/admin/change'
app.config['SECURITY_USER_IDENTITY_ATTRIBUTES'] = ['email', 'username']

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
security = Security(app, user_datastore)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


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


# Views
api.init_app(app)
admin.add_view(RiffAdminView(Riff, db_session))
admin.add_view(RiffExerciseAdminView(RiffExercise, db_session))
admin.add_view(UserAdminView(User, db_session))
admin.add_view(RolesAdminView(Role, db_session))
migrate = Migrate(app, db=db_session) # T
logger.info("Ready loading admin views and api")


if __name__ == '__main__':
    app.run()
