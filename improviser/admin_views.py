from flask import flash
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_security import utils
from markupsafe import Markup
from database import Riff
from sqlalchemy import String
from wtforms import PasswordField


class UserAdminView(ModelView):
    # Don't display the password on the list of Users
    column_exclude_list = list = ('password',)

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True
    can_set_page_size = True

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
    Riff.image = String
    column_list = ['id', 'name', 'render_valid', 'render_date', 'notes', 'chord_info', 'multi_chord',
                   'number_of_bars', 'chord', 'created_date', 'image']
    column_default_sort = ('name', True)
    column_filters = ('render_valid', 'number_of_bars', 'chord')
    column_searchable_list = ('id', 'name', 'chord', 'notes', 'number_of_bars')
    can_set_page_size = True

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
        except Exception as error:
            if not self.handle_view_exception(error):
                flash('Failed to schedule re-render riff. {error}'.format(error=str(error)))

    def _list_thumbnail(view, context, model, name):
        return Markup(f'<img src="https://www.improviser.education/static/rendered/80/riff_{model.id}_c.png">')

    column_formatters = {
        'image': _list_thumbnail
    }


class RiffExerciseAdminView(ModelView):
    column_list = ['id', 'name', 'is_global', 'created_by', 'created_at']
    column_default_sort = ('name', True)
    column_searchable_list = ('id', 'name', 'created_by')
    can_set_page_size = True

    def is_accessible(self):
        if 'admin' in current_user.roles:
            return True


class BaseAdminView(ModelView):

    # Prevent administration of Tags unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        if 'admin' in current_user.roles:
            return True

