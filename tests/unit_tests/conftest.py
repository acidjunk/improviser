import os
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

from improviser.database import db, user_datastore
# from improviser.main import db_migrations


@pytest.fixture(scope="session")
def database(db_uri):
    """Create and drop test database for a pytest worker."""
    url = make_url(db_uri)
    db_to_create = url.database

    # database to connect to for creating `db_to_create`.
    url.database = "postgres"
    engine = create_engine(str(url))

    with closing(engine.connect()) as conn:
        # Can't drop or create a database from within a transaction; end transaction by committing.
        conn.execute("COMMIT;")
        conn.execute(f'DROP DATABASE IF EXISTS "{db_to_create}";')
        conn.execute("COMMIT;")
        conn.execute(f'CREATE DATABASE "{db_to_create}";')
    try:
        yield
    finally:
        with closing(engine.connect()) as conn:
            conn.execute("COMMIT;")
            conn.execute(f'DROP DATABASE IF EXISTS "{db_to_create}";')


@pytest.fixture(scope="session")
def db_uri(worker_id):
    """Ensure that every py.test workerthread uses a own DB, when running the test suite with xdist and `-n auto`."""
    database_uri = os.environ.get("DATABASE_URI", "postgresql://improviser:improviser@localhost/improviser-test")
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


@pytest.fixture(scope='session')
def flask_app(monkeysession, database, db_uri):
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
    # with app.app_context():
    #     # db_migrations()
    #     try:
    #         yield app
    #     finally:
    #         print("Finally")
    #         db.drop_all()
    #         # In addition to dropping all model backed tables we need to drop the Alembic specific table. Without it
    #         # Alembic thinks it doesn't need to run any migrations on the next test run.
    #         db.engine.connect(close_with_result=True).execute("DROP TABLE alembic_version;")
    #         # Drop all connection, so that the database can be dropped
    #         db.engine.dispose()


    # migrate = Migrate(app, db)
    # with app.app_context():
    #     # Normally one would create all model backed tables using `db.create_all()`. However we have delegated that
    #     # task to Alembic.
    #     db_migrations()
    #     try:
    #         yield app
    #     finally:
    #         db.drop_all()
    #         # In addition to dropping all model backed tables we need to drop the Alembic specific table. Without it
    #         # Alembic thinks it doesn't need to run any migrations on the next test run.
    #         db.engine.connect(close_with_result=True).execute("DROP TABLE alembic_version;")
    #         # Drop all connection, so that the database can be dropped
    #         db.engine.dispose()

    return app


@pytest.fixture(autouse=True)
def sqlalchemy(flask_app, monkeypatch):
    """Ensure tests are run in a transaction with automatic rollback.

    As most tests require access to the database either directly or indirectly we've set `autouse=True`. This will
    have a performance impact on tests that don't need the database, though it makes writing most tests easier by not
    have to add a `sqlalchemy` parameter to each test' function signature.

    This implementation creates a connection and transaction before yielding to the test function. Any transactions
    started and committed from within the test will be tied to this outer transaction. From the test function's
    perspective it looks like everything will indeed be committed; allowing for queries on the database to be
    performed to see if functions under test have persisted their changes to the database correctly. However once
    the test function returns this fixture will clean everything up by rolling back the outer transaction; leaving the
    database in a known state (=empty with the exception of what migrations have added as the initial state).

    Implementation is based on comment https://github.com/mitsuhiko/flask-sqlalchemy/pull/249#issuecomment-141720626

    Args:
        flask_app: fixture for providing the application context and an initialized database. Although specifying this
            as an explicit parameter is redundant due to `flask_app`'s autouse setting, we have made the dependency
            explicit here for the purpose of documentation.
        monkeypatch: fixture for monkeypatching.

    Yields:
        SQLAlchemy: SQLAlchemy object (normally referenced in application under the name `db` as in `db.session...`

    """
    connection = db.engine.connect()
    transaction = connection.begin()

    # Patch Flask-SQLAlchemy to use our connection
    monkeypatch.setattr(db, "get_engine", lambda *args: connection)

    try:
        yield db
    finally:
        db.session.remove()
        transaction.rollback()
        connection.close()






def db_migrations():
    migrations_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../improviser/migrations/")
    from alembic.config import Config
    config = Config(migrations_dir + "alembic.ini")
    config.set_main_option("sqlalchemy.url", current_app.config.get("SQLALCHEMY_DATABASE_URI"))
    config.set_main_option("script_location", migrations_dir)
    command.upgrade(config, "head")
