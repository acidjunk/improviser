import datetime
import hashlib
import os
import uuid

import pytest
from contextlib import closing

from flask import Flask
from flask_login import LoginManager
from flask_security import Security
from security import ExtendedRegisterForm, ExtendedJSONRegisterForm
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url

from improviser.database import (
    db, user_datastore, Riff, Instrument, UserPreference, Role, User, RiffExercise,
    RiffExerciseItem
)

STUDENT_EMAIL = 'student@example.com'
STUDENT_PASSWORD = 'STUDENTJE'
TEACHER_EMAIL = 'teacher@example.com'
TEACHER_PASSWORD = 'TEACHERTJE'

QUICK_TOKEN = 'da564af5-3767-48c0-acdc-7b610293fd72'
QUICK_TOKEN_MD5 = hashlib.md5(QUICK_TOKEN.encode('utf-8')).hexdigest()


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
    if os.getenv("DB_USER"):
        print("Running with TRAVIS!")
        database_uri = "postgresql://postgres:@localhost/improviser-test"
    if worker_id == "master":
        # pytest is being run without any workers
        print(f"USING DB CONN: {database_uri}")
        return database_uri
    # using xdist setup
    url = make_url(database_uri)
    url.database = f"{url.database}-{worker_id}"
    print(f"USING DB CONN: {url}")
    return str(url)


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
    app.config['TESTING'] = True

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
    api.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

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

    # here we go
    yield app

    # clean up : revert DB to a clean state
    db.session.remove()
    db.session.commit()
    db.session.close_all()
    db.drop_all()
    db.engine.dispose()


@pytest.fixture
def instruments():
    instrument_1 = Instrument(
        id=str(uuid.uuid4()),
        name='Generic C',
        root_key='c'
    )
    instrument_2 = Instrument(
        id=str(uuid.uuid4()),
        name='Tenor sax"',
        root_key='bes'
    )
    db.session.add(instrument_1)
    db.session.add(instrument_2)
    db.session.commit()
    return [instrument_1, instrument_2]


@pytest.fixture
def user_roles():
    roles = ["student", "member", "teacher", "operator", "moderator", "admin"]
    [db.session.add(Role(id=str(uuid.uuid4()), name=role)) for role in roles]
    db.session.commit()


@pytest.fixture
def student_unconfirmed(instruments, user_roles):
    user = user_datastore.create_user(username='student', password=STUDENT_PASSWORD, email=STUDENT_EMAIL)
    user_datastore.add_role_to_user(user, "student")
    user_preference = UserPreference(instrument_id=instruments[0].id, user_id=user.id)
    db.session.add(user_preference)
    db.session.commit()
    return user


@pytest.fixture
def student(student_unconfirmed):
    user = User.query.filter(User.email == STUDENT_EMAIL).first()
    user.confirmed_at = datetime.datetime.utcnow()
    db.session.commit()
    return user


@pytest.fixture
def student_logged_in(student):
    user = User.query.filter(User.email == STUDENT_EMAIL).first()
    user.quick_token = QUICK_TOKEN_MD5
    user.quick_token_created_at = datetime.datetime.now()
    db.session.commit()
    return user


@pytest.fixture
def teacher_unconfirmed(instruments, user_roles):
    user = user_datastore.create_user(username='teacher', password=TEACHER_PASSWORD, email=TEACHER_EMAIL)
    user_datastore.add_role_to_user(user, "teacher")
    user_preference = UserPreference(instrument_id=instruments[0].id, user_id=user.id)
    db.session.add(user_preference)
    db.session.commit()
    return user


@pytest.fixture
def teacher(teacher_unconfirmed):
    user = User.query.filter(User.email == TEACHER_EMAIL).first()
    user.confirmed_at = datetime.datetime.utcnow()
    db.session.commit()
    return user


@pytest.fixture
def teacher_logged_in(teacher):
    user = User.query.filter(User.email == TEACHER_EMAIL).first()
    user.quick_token = QUICK_TOKEN_MD5
    user.quick_token_created_at = datetime.datetime.now()
    db.session.commit()
    return user


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


@pytest.fixture
def riff_unrendered():
    riff = Riff(
        id=str(uuid.uuid4()),
        name="Major 9 chord up down unrendered",
        number_of_bars=1,
        notes="c'8 e' g' b' d'' b' g' e'",
        chord='CM9',
        chord_info='c1:maj9',
        render_valid=False,
    )
    db.session.add(riff)
    db.session.commit()
    return riff


@pytest.fixture
def riff_multi_chord():
    riff = Riff(
        id=str(uuid.uuid4()),
        name="Bebop riff on 2-5-1 in 2 bars",
        number_of_bars=1,
        notes="""g''8 fis'' e'' a'' e''4 d''8 g'' \bar "|" g''2 r2""",
        chord_info='d2:m7 g:7 c1:maj7',
        multi_chord=True,
        render_valid=True,
        render_date=datetime.datetime.utcnow(),
    )
    db.session.add(riff)
    db.session.commit()
    return riff


@pytest.fixture
def riff_without_chord_info():
    riff = Riff(
        id=str(uuid.uuid4()),
        name="Major sixth up with chord",
        number_of_bars=1,
        notes="""c'2 a'""",
        chord="CM",
        multi_chord=False,
        render_valid=True,
        render_date=datetime.datetime.utcnow(),
    )
    db.session.add(riff)
    db.session.commit()
    return riff


@pytest.fixture
def riff_without_chord():
    riff = Riff(
        id=str(uuid.uuid4()),
        name="Major sixth up with chord_info",
        number_of_bars=1,
        notes="""c'2 a'""",
        chord_info="c1:maj",
        multi_chord=False,
        render_valid=True,
        render_date=datetime.datetime.utcnow(),
    )
    db.session.add(riff)
    db.session.commit()
    return riff


@pytest.fixture
def exercise_1(teacher, riff, riff_multi_chord, riff_without_chord_info, riff_without_chord):
    exercise_id = str(uuid.uuid4())
    riff_exercise = RiffExercise(
        id=exercise_id,
        name="Exercise 1",
        description="Some description",
        root_key="c",
        instrument_key="c",
        is_public=True,
        is_copyable=True,
        # starts=3,
        created_by=teacher.id
    )
    db.session.add(riff_exercise)
    record = RiffExerciseItem(id=str(uuid.uuid4()), riff_id=riff.id, riff_exercise_id=exercise_id,
                              number_of_bars=riff.number_of_bars, chord_info=riff.chord_info,
                              pitch="c", octave=0, order_number=0)
    db.session.add(record)
    db.session.commit()
    return riff_exercise


@pytest.fixture
def exercise_2(teacher, riff, riff_multi_chord, riff_without_chord_info, riff_without_chord):
    riff_exercise = RiffExercise(
        id=str(uuid.uuid4()),
        name="Exercise 1",
        description="Some description",
        root_key="c",
        instrument_key="c",
        is_public=True,
        is_copyable=True,
        # starts=3,
        created_by=teacher.id
    )
    db.session.add(riff_exercise)
    db.session.commit()
    return riff_exercise
