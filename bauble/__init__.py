from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from importlib import import_module
import logging
import os

import flask
from flask import Blueprint, Flask, json
from flask_appconfig import AppConfig, HerokuConfig
from flask_appconfig.env import from_envvars
from flask.ext.babel import Babel
from flask.ext.mail import Mail
from flask.ext.migrate import Migrate
from flask.ext.login import LoginManager
from flask.ext.sslify import SSLify
from werkzeug.routing import BaseConverter

class JSONEncoder(flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return int(obj.replace(tzinfo=timezone.utc).timestamp() * 1000)
        if isinstance(obj, date):
            return str(obj.isoformat())
        if isinstance(obj, Decimal):
            return float(obj)
        else:
            return super().default(obj)


class RegexConverter(BaseConverter):
    """URL Map converter that allows matching regex string for routes"""
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


class Request(flask.Request):

    @property
    def prefers_json(self):
        return self.path.endswith('.json') or self.accept_mimetypes.best == 'application/json'

    @property
    def is_json(self):
        # The flask docs say this is added in 0.11
        return self.mimetype == 'application/json'

    @property
    def params(self):
        return self.get_json() if self.is_json else self.values


def create_app(config_filename=None):
    app = Flask(__name__)
    app.request_class = Request
    app.url_map.converters['re'] = RegexConverter

    if config_filename is None:
        HerokuConfig(app)
    else:
        AppConfig(app, config_filename)

    from_envvars(app.config, prefix='')
    app.debug = app.config.get('DEBUG')

    # TODO: these variables probably aren't unjsonnable anymore

    # push all variables into the environment
    unjsonnable = (datetime, timedelta)
    data = {k: json.dumps(v) for k, v in app.config.items() if not isinstance(v, unjsonnable)}
    os.environ.update(data)

    # app.logger.info('App is running on port %s', os.environ.get('PORT'))

    if app.config['DEBUG'] is not True:
        log_level = app.config.get('LOG_LEVEL', 'DEBUG')
        app.logger.setLevel(getattr(logging, log_level.upper()))

    import bauble.db as db

    if 'LOG_SQL' in os.environ:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    db.init_app(app)

    # register flask extensionsa
    SSLify(app, permanent=True)
    app.login_manager = LoginManager(app)
    app.login_manager.login_view = "auth.login"
    app.mail = Mail(app)
    app.babel = Babel(app)

    from .assets import init_app
    init_app(app)


    # TODO: just import everything controllers

    for controller in ['auth', 'index', 'batch']:
        module = import_module('bauble.controllers.{}'.format(controller))
        app.register_blueprint(module.blueprint)

    from bauble.resource import Resource
    for controller in ['search', 'family', 'genus', 'taxon']:
        module = import_module('bauble.controllers.{}'.format(controller))
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            # find all the blueprints in the files
            if isinstance(attr, Blueprint):
                app.register_blueprint(attr)
            # if isclass(attr) and issubclass(attr, Blueprint) and attr != Resource:
            #     app.register_blueprint(attr())

    from bauble.controllers.api import api
    app.register_blueprint(api)

    from bauble.error import init_errorhandlers
    init_errorhandlers(app)

    app.json_encoder = JSONEncoder

    return app
