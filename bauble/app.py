# from datetime import datetime, timedelta
# import locale
# import logging
# import os
# import sys

# from celery import Celery
# from flask import Flask, json
# from flask_appconfig import AppConfig, HerokuConfig
# from flask_appconfig.env import from_envvars
# from flask.ext.migrate import Migrate
# from flask.ext.login import LoginManager

# if sys.platform == 'darwin':
#     locale.setlocale(locale.LC_ALL, 'en_US')
# else:
#     locale.setlocale(locale.LC_ALL, 'en_US.utf8')


# if 'DYNO' in os.environ:
#     # Heroku
#     config_filename = None
# else:
#     config_filename = '../env/local.py'


# def currency_filter(value, units='pennies'):
#     if units == 'pennies':
#         value = round(value / 100, 2)

#     return locale.currency(value)


# def init_app(app):
#     if app.config['DEBUG'] is not True:
#         log_level = app.config.get('LOG_LEVEL', 'DEBUG')
#         app.logger.setLevel(getattr(logging, log_level.upper()))

#     import bauble.db as db

#     if 'LOG_SQL' in os.environ:
#         logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

#     db.init_app(app)
#     db.ma.init_app(app)
#     Migrate(app, db)

#     app.login_manager = LoginManager(app)

#     from .assets import init_app
#     init_app(app)

#     from bauble.controllers import blueprint
#     app.register_blueprint(blueprint)

#     from bauble.error import init_errorhandlers
#     init_errorhandlers(app)


# def create_app(config_filename=None):
#     app = Flask(__name__)
#     app.debug = True

#     if config_filename is None:
#         HerokuConfig(app)
#     else:
#         AppConfig(app, config_filename)

#     from_envvars(app.config, prefix='')

#     # push all variables into the environment
#     unjsonnable = (datetime, timedelta)
#     data = {k: json.dumps(v) for k, v in app.config.items() if not isinstance(v, unjsonnable)}
#     os.environ.update(data)

#     app.logger.info('App is running on port %s', os.environ.get('PORT'))
#     return app


# def create_celery_app(flask_app):
#     # *** BROKER_URL works but not CELERY_BROKER_URL, maybe b/c its in the environ ?????
#     celery = Celery(flask_app.import_name, broker=flask_app.config['BROKER_URL'])
#     celery.conf["CELERY_ACCEPT_CONTENT"] = ['pickle']
#     celery.conf.update(flask_app.config)
#     TaskBase = celery.Task

#     class ContextTask(TaskBase):
#         abstract = True

#         def __call__(self, *args, **kwargs):
#             with flask_app.app_context():
#                 return TaskBase.__call__(self, *args, **kwargs)

#     celery.Task = ContextTask
#     return celery


# app = create_app(config_filename)
# celery = create_celery_app(app)
# init_app(app)
