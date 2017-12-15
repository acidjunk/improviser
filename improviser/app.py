import datetime
import uuid

import os
from flask import Flask, flash
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask_migrate import Migrate, MigrateCommand
from flask_restplus import Api, Resource, fields, marshal_with
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql.base import UUID


from render.render import Render

VERSION = '0.1.0'

app = Flask(__name__)
app.secret_key = 'TODO:MOVE_TO_BLUEPRINT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://improviser:improviser@localhost/improviser'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# setup DB
db = SQLAlchemy(app)
db.UUID = UUID

api = Api(app)
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
admin = Admin(app, name='Improviser', template_mode='bootstrap3')


@app.context_processor
def version():
    return dict(version=VERSION)


riff_fields = {
    'id': fields.String,
    'name': fields.String,
    'number_of_bars': fields.Integer,
    'notes': fields.String,
    'chord': fields.String,
    'image': fields.String,
    'render_valid': fields.Boolean,
    'render_date': fields.DateTime,

}


class Riff(db.Model):
    __tablename__ = 'riffs'
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = db.Column(db.String(255), unique=True, index=True)
    number_of_bars = db.Column(db.Integer())
    notes = db.Column(db.String(255))
    chord = db.Column(db.String(255), index=True)
    render_valid = db.Column(db.Boolean, default=False)
    render_date= db.Column(db.DateTime)

    def __repr__(self):
        return '<Riff %r>' % self.name


@api.route('/api/riffs')
class RiffListResource(Resource):

    @marshal_with(riff_fields)
    def get(self):
        riffs = Riff.query.all()
        for riff in riffs:
            riff.image = f'http://127.0.0.1:5000/static/rendered/large/riff_{riff.id}_c.png'
        return riffs

@api.route('/api/populate')
class PopulateAppResource(Resource):

    def get(self):
        # Some fun stuff popular
        lily = []
        lily.append(("fis''8 e''16 b'8 g' fis''. e''16 b'8 g'8.", "medium", 1, "Careless whisper 1"))
        lily.append(("d''8 c''16 g'8 e' d''. c''16 g'4..", "medium", 1, "Careless whisper 2"))
        lily.append(("c''8 b'16 g'8 e'. c'2", "medium", 1, "Careless whisper 3"))
        lily.append(("b8 c' d' e' fis' g' a' b'", "medium", 1, "Careless whisper 4"))

        # minor riffs only
        lily.append(("bes'8. bes'16 r4 bes'8. bes'16 r4 r8 bes'8 c''16 bes'8 es''16 r2", "medium", 2, "Funk 1"))
        lily.append(("r4 es''16 d''8 c''16 c''8 bes'8 r4 bes'8 r16 bes'16 r4 r8 c''16 r16 r4", "medium", 2, "Funk 2"))

        # easy
        lily.append(("c' d' ees' f' g' aes' b' c'' c'' d'' ees'' f'' g'' ges'' b'' c'''", "easy", 2,
                     "natural harmonic minor easy"))
        lily.append(("c' d' ees' f' g' a' b' c'' c'' d'' ees'' f'' g'' a'' b'' c'''", "easy", 2,
                     "natural melodic minor easy"))  # TODO: implement some smart stuff get a correct reversed scale
        lily.append(("c' d' ees' f' g' a' bes' c'' c'' d'' ees'' f'' g'' a'' bes'' c'''", "easy", 2, "dorian easy"))
        lily.append(("c' des' ees' f' g' a' bes' c''", "easy", 2, "phrygian easy"))

        lily.append(("c' ees' g' ees' g' c'' g' c'' ees'' c'' ees'' g'' ees'' g'' c'''2", "easy", 4,
                     "minor broken chord easy"))
        lily.append(("c'4 ees' f' fis' g' bes' c''2 c''4 ees'' f'' fis'' g'' bes''4 c'''2", "medium", 2,
                     "minor blues scale easy"))

        # medium
        lily.append(("c'4 d'8 ees' f' g' aes' bes' c''4 d''8 ees'' f'' g'' aes'' bes''8", "medium", 2,
                     "minor plain scale medium"))
        lily.append(("c'8 ees' g' ees' g' c'' g' c'' ees'' c'' ees'' g'' ees'' g''8 c'''4", "medium", 2,
                     "minor broken chord medium"))
        lily.append(("c'4 ees'8 f' fis' g' bes'4 c''4 ees''8 f'' fis'' g''8 bes''4", "medium", 2,
                     "minor blues scale medium"))

        # hard
        lily.append(("c'8 f' bes' ees'' c'' f'' a'' g'' ees'' des'' aes' ges' b' a' e' d'8", "hard", 2,
                     "fourths in key in & out hard"))
        lily.append(("f' c' f' g' aes' ees' aes' bes' b' e'' cis'' fis'' b'' e''' cis''' a'' gis'' cis''' ais'' dis''' "
                     "c'' g'' f'' bes'' a'' e'' a'' g'' d'' a' g' c''", "hard", 4, "fourths in key in & out hard"))
        lily.append(("c'8 f' bes' g' c'' f'' d'' g'' c''' d''' a'' e'' d'' g'' f'' c''8", "hard", 2,
                     "fourths in key hard"))

        for li in lily:
            riff = Riff(name=li[3], number_of_bars=li[2], notes=li[0], chord=li[1])
            try:
                db.session.add(riff)
                db.session.commit()
                print(f"Added {riff.name}")
            except Exception as error:
                db.session.rollback()
                print(f"Skipped duplicate {riff.name}")


@api.route('/api/render/all')
class RenderRiff(Resource):

    def get(self):
        riffs = Riff.query.all()
        for riff in riffs:
            print(riff)

            render_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static',
                                       'rendered')
            myRenderer = Render(render_path)
            keys = ['c']  # only c for now
            for key in keys:
                myRenderer.name = "riff_%s_%s" % (riff.id, key)
                notes = riff.notes.split(" ")
                myRenderer.addNotes(notes)
                myRenderer.set_cleff('treble')
                myRenderer.doTranspose(key)
                if not myRenderer.render():
                    print(f"Error: couldn't render riff.id: {riff.id}")

            # internal bookkeeping
            riff.render_date = datetime.datetime.now()
            riff.render_valid = True
            db.session.commit()


class RiffAdminView(ModelView):
    column_default_sort = ('name', True)
    column_filters = ('number_of_bars', 'chord')
    column_searchable_list = ('name', 'chord')

    @action('render', 'Render', 'Are you sure you want to re-render selected riffs?')
    def action_approve(self, ids):
        try:
            query = Riff.query.filter(Riff.id.in_(ids))
            count = 0
            for riff in query.all():
                print(riff)
            flash('{} render of riffs successfully rescheduled.'.format(count))
        except Exception as error:
            if not self.handle_view_exception(error):
                flash('Failed to re-render riff. {error}'.format(error=str(error)))


admin.add_view(RiffAdminView(Riff, db.session))

if __name__ == '__main__':
    manager.run()
