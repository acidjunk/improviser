from flask import Blueprint
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin

class AdminBlueprint(Blueprint):
    views=None

    def __init__(self, *args, **kargs):
        self.views = []
        return super(AdminBlueprint, self).__init__('admin2', __name__,url_prefix='/admin2')


    def add_view(self, view):
        self.views.append(view)

    def register(self, app, options, first_registration=False):
        print(app)
        admin = Admin(app, name='iMproviser', template_mode='adminlte')

        for v in self.views:
            admin.add_view(v)

        return super(AdminBlueprint, self).register(app, options, first_registration)