import os
import sys
from flask import render_template

from .config import Config
from .app_template import AppTemplate

# apps is a special folder where you can place your blueprints
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_PATH, "apps"))

basestring = getattr(__builtins__, 'basestring', str)


class App(AppTemplate):
    def configure_views(self):
        @self.route('/')
        def index_view():
            return render_template("index.html")


def config_str_to_obj(cfg):
    if isinstance(cfg, basestring):
        module = __import__('config', fromlist=[cfg])
        return getattr(module, cfg)
    return cfg


def app_factory(config, app_name, blueprints=None):
    # you can use AppTemplate directly if you wish
    app = App(app_name, template_folder=os.path.join(PROJECT_PATH, 'templates'))
    # config = config_str_to_obj(config)
    config = Config
    app.configure(config)
    app.add_blueprint_list(blueprints or config.BLUEPRINTS)
    app.setup()

    return app
