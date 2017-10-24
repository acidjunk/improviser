import uuid

from flask import Flask
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask_migrate import Migrate, MigrateCommand
from flask_restplus import Api, Resource, fields, marshal_with
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

VERSION = '0.1.0'

app = Flask(__name__)
app.secret_key = 'TODO:MOVE_TO_BLUEPRINT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://improviser:improviser@localhost/improviser'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
admin = Admin(app, name='Improviser', template_mode='bootstrap3')


@app.context_processor
def version():
    return dict(version=VERSION)


riff_fields = {
    'name': fields.String,
    'number_of_bars': fields.Integer,
    'notes': fields.String,
    'chord': fields.String,
}


class Riff(db.Model):
    __tablename__ = 'riffs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, index=True)
    number_of_bars = db.Column(db.Integer())
    notes = db.Column(db.String(255))
    chord = db.Column(db.String(255), index=True)

    def __repr__(self):
        return '<Riff %r>' % self.name


@api.route('/api/riffs')
class RiffListResource(Resource):

    @marshal_with(riff_fields)
    def get(self):
        riffs = Riff.query.all()
        return riffs


class RiffAdminView(ModelView):
    column_default_sort = ('name', True)
    column_filters = ('number_of_bars', 'chord')
    column_searchable_list = ('name', 'chord')


admin.add_view(RiffAdminView(Riff, db.session))

if __name__ == '__main__':
    manager.run()
