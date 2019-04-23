import datetime
import os
import uuid

import pytest
from _pytest.monkeypatch import MonkeyPatch
from contextlib import contextmanager, closing

from alembic import command
from flask import Flask, current_app
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_security import Security
from security import ExtendedRegisterForm, ExtendedJSONRegisterForm
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
# from urllib3_mock import Responses

from improviser.database import db, user_datastore, Riff
# from improviser.main import db_migrations
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def database(db_uri):
    """Create and drop test database for a pytest worker."""
    url = make_url(db_uri)
    db_to_create = url.database

    # database to connect to for creating `db_to_create`.
    url.database = "postgres"
    engine = create_engine(str(url))

    with closing(engine.connect()) as conn:
        print(f"Drop and create {db_to_create}")
        # Can't drop or create a database from within a transaction; end transaction by committing.
        conn.execute("COMMIT;")
        conn.execute(f'DROP DATABASE IF EXISTS "{db_to_create}";')
        conn.execute("COMMIT;")
        conn.execute(f'CREATE DATABASE "{db_to_create}";')
        print(f"Drop and create done for {db_to_create}")
    yield database


# @pytest.fixture
# def database(db_uri):
#     """Create and drop test database for a pytest worker."""
#     # url = make_url(db_uri)
#     # db_to_create = url.database
#     #
#     # # database to connect to for creating `db_to_create`.
#     # url.database = "postgres"
#     # engine = create_engine(str(url))
#     # with closing(engine.connect()) as conn:
#     #     print(f"Drop and create {db_to_create}")
#     #     # Can't drop or create a database from within a transaction; end transaction by committing.
#     #     conn.execute("COMMIT;")
#     #     conn.execute(f'DROP DATABASE IF EXISTS "{db_to_create}";')
#     #     conn.execute("COMMIT;")
#     #     conn.execute(f'CREATE DATABASE "{db_to_create}";')
#     #     print(f"Drop and create done for {db_to_create}")
#     pass



@pytest.fixture(scope="session")
def db_uri(worker_id):
    """Ensure that every py.test workerthread uses a own DB, when running the test suite with xdist and `-n auto`."""
    database_uri = "postgresql://improviser:improviser@localhost/improviser-test"
    if worker_id == "master":
        # pytest is being run without any workers
        print(f"USING DB CONN: {database_uri}")
        return database_uri
    url = make_url(database_uri)
    url.database = f"{url.database}-{worker_id}"
    return str(url)


@pytest.fixture(scope="session")
def monkeysession():
    """Monkeypatch fixture with session scope.

    The `monkeypatch` fixture has `function` scope and as such cannot be used in other fixtures that have a broader
    scope (eg. `module` or even `session`). This fixture adapts the monkey patching duration to the session scope.
    """
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="function")
def app(database, db_uri):
    """
    Create a Flask app context for the tests.
    """

    # Todo -> move to separate config class and use it in main and tests
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') if os.getenv('SECRET_KEY') else 'super-secret'

    app.config['FLASK_ADMIN_SWATCH'] = 'flatly'
    app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
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
    # mail = Mail()
    app.app_context().push()

    from apis import api
    # api.init_app(app)
    db.init_app(app)
    # mail.init_app(app)

    db.create_all()

    yield app

    # Clean up : revert DB to a clean state
    db.session.remove()
    db.session.commit()
    db.session.close_all()
    db.drop_all()
    # Base.metadata.drop_all(self._engine)
    db.engine.dispose()


@pytest.fixture
def riff():
    riff = Riff(
        id=str(uuid.uuid4()),
        name="Major 9 chord up down",
        number_of_bars=1,
        notes="c'8 e' g' b' d'' b' g' e'",
        chord='CM9',
        chord_info='c1:maj9',
        render_valid=True,
        render_date=datetime.datetime.utcnow(),
    )
    db.session.add(riff)
    db.session.commit()
    return riff
