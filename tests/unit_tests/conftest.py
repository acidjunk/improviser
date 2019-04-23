import os

import pytest
import sqlalchemy as sa
from flask_migrate import Migrate, command

from database import user_datastore, User
from flask import Flask, current_app
from flask_login import LoginManager
from flask_mail import Mail
from flask_security import Security
from flask_sqlalchemy import SQLAlchemy
from pytest_postgresql.factories import init_postgresql_database, drop_postgresql_database

# Retrieve a database connection string from the shell environment
from security import ExtendedRegisterForm, ExtendedJSONRegisterForm

try:
    DB_CONN = os.environ['TEST_DATABASE_URL']
except KeyError:
    raise KeyError('TEST_DATABASE_URL not found. You must export a database ' +
                   'connection string to the environmental variable ' +
                   'TEST_DATABASE_URL in order to run tests.')
else:
    DB_OPTS = sa.engine.url.make_url(DB_CONN).translate_connect_args()


@pytest.fixture(scope='session')
def database(request):
    """
    Create a Postgres database for the tests, and drop it when the tests are done.
    """
    pg_host = DB_OPTS.get("host")
    pg_port = DB_OPTS.get("port")
    pg_user = DB_OPTS.get("username")
    pg_db = DB_OPTS["database"]

    init_postgresql_database(pg_user, pg_host, pg_port, pg_db)
    # os.system('psql -d improviser_test < tests/unit_tests/empty_db.psql')

    @request.addfinalizer
    def drop_database():
        drop_postgresql_database(pg_user, pg_host, pg_port, pg_db, 9.6)


@pytest.fixture(scope='session')
def app(database):
    """
    Create a Flask app context for the tests.
    """
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONN

    # Todo -> move to separate config class and use it in main and tests
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') if os.getenv('SECRET_KEY') else 'super-secret'

    app.config['FLASK_ADMIN_SWATCH'] = 'flatly'
    app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') if os.getenv('SECRET_KEY') else 'super-secret'
    app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha256'
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT') if os.getenv('SECURITY_PASSWORD_SALT') \
        else 'SALTSALTSALT'

    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Replace the next six lines with your own SMTP server settings
    # Todo -> use local mailling during tests?
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
    # Todo -> check if we can fix this without completely disabling it: it's only needed when login request is not via .json
    app.config['WTF_CSRF_ENABLED'] = False


    security = Security(app, user_datastore, register_form=ExtendedRegisterForm,
                        confirm_register_form=ExtendedJSONRegisterForm)
    login_manager = LoginManager(app)
    mail = Mail()

    return app


@pytest.fixture(scope='session')
def _db(app):
    """
    Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
    database connection.
    """
    db = SQLAlchemy(app=app)

    return db


def db_migrations():
    migrations_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "improviser/migrations/")
    from alembic.config import Config
    config = Config(migrations_dir + "alembic.ini")
    config.set_main_option("sqlalchemy.url", current_app.config.get("SQLALCHEMY_DATABASE_URI"))
    config.set_main_option("script_location", migrations_dir)
    command.upgrade(config, "head")
