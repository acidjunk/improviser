import hashlib
from database import User
from flask import request, current_app
from flask_security.decorators import _get_unauthorized_response
from flask_security.forms import RegisterForm, ConfirmRegisterForm
from functools import wraps
from werkzeug.local import LocalProxy
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

_security = LocalProxy(lambda: current_app.extensions['security'])

class ExtraUserFields():
    username = StringField('Username', [DataRequired()])
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])
    mail_offers = BooleanField('May we mail you about new offers?',
                               false_values={False, 'false', ''})
    mail_announcements = BooleanField('May we mail you about platform announcements?',
                                      false_values={False, 'false', ''}, default='true')


class ExtendedRegisterForm(RegisterForm, ExtraUserFields):
    pass


class ExtendedJSONRegisterForm(ConfirmRegisterForm, ExtraUserFields):
    pass


def check_quick_token():
    quick_token = request.headers.get("Quick-Authentication-Token")
    if not quick_token:
        return False

    try:
        user_id, token = quick_token.split(":")
    except:
        return False

    quick_token_md5 = hashlib.md5(token.encode('utf-8')).hexdigest()
    user = User.query\
        .filter(User.id == user_id)\
        .filter(User.quick_token == quick_token_md5) \
        .first()
    if user:
        return True
    return False


def quick_token_required(fn):
    """Decorator that protects endpoints using token authentication. The token
    should be added to the request by the client by using a query string
    variable with a name equal to the configuration value of
    `SECURITY_TOKEN_AUTHENTICATION_KEY` or in a request header named that of
    the configuration value of `SECURITY_TOKEN_AUTHENTICATION_HEADER`
    """

    @wraps(fn)
    def decorated(*args, **kwargs):
        print(request)
        if check_quick_token():
            return fn(*args, **kwargs)
        if _security._unauthorized_callback:
            return _security._unauthorized_callback()
        else:
            return _get_unauthorized_response()
    return decorated
