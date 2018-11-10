from flask_restplus import Api

from .v1.riffs import api as riffs_ns

api = Api(
    title='iMproviser API',
    version='1.0',
    description='A restful api for the iMproviser',
)

api.add_namespace(riffs_ns, path='/v1/riffs')
