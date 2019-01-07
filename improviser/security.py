from flask_security.forms import RegisterForm, ConfirmRegisterForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired


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
