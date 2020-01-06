from flask_restplus import Api

from .v1.backing_tracks import api as backing_tracks_ns
from .v1.exercises import api as exercises_ns
from .v1.lessons import api as lessons_ns
from .v1.riffs import api as riffs_ns
from .v1.tags import api as tags_ns
from .v1.users import api as users_ns

api = Api(
    title='iMproviser API',
    version='1.0',
    description='A restful api for the iMproviser',
)
api.add_namespace(backing_tracks_ns, path='/v1/backing-tracks')
api.add_namespace(riffs_ns, path='/v1/riffs')
api.add_namespace(tags_ns, path='/v1/tags')
api.add_namespace(exercises_ns, path='/v1/exercises')
api.add_namespace(lessons_ns, path='/v1/lessons')
api.add_namespace(users_ns, path='/v1/users')
