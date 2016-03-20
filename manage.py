#!/usr/bin/env python
# coding: utf-8

from datetime import datetime, timedelta
from importlib import import_module
import os
import pathlib
import sys
import subprocess

import requests
from flask.ext.assets import ManageAssets
from flask.ext.migrate import MigrateCommand
from flask.ext.script import Manager
from flask import json

from bauble import create_app
from bauble.assets import webassets

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    config_filename = '../env/test.py'
elif 'DYNO' in os.environ:
    # heroku
    config_filename = None
else:
    config_filename = '../env/local.py'

app = create_app(config_filename)
manager = Manager(app)
manager.add_command("assets", ManageAssets(webassets))
manager.add_command("db", MigrateCommand)


def sh(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    """Run a shell command."""
    try:
        return subprocess.check_call(cmd, stdin=stdin, stdout=stdout, stderr=stderr,
                                     shell=True)
    except subprocess.CalledProcessError as exc:
        print("** Error running command: {}".format(cmd))
        print(exc)
        sys.exit(exc.returncode)


@manager.command
@manager.option('-v', '--verbose', default=False)
def herokucfg(environment, verbose=False):
    """Push a section of config.yaml to Heroku config.

    The config is set using an HTTP request instead of using the Heroku toolbelt so
    that it can be more easily done from a Travis build environment.

    If api_key is not passed then the key is read automatically from ~/.netrc
    which is set by the heroku login command.
    """
    # create an app for a specific environment

    env_module = import_module('env.{}'.format(environment))
    sync_keys = filter(lambda s: not s.startswith('_'), dir(env_module))

    data = {}
    unjsonnable = (datetime, timedelta)
    for key in sync_keys:
        val = getattr(env_module, key)
        # TODO: for now filter out unjsonnable values until we can patch
        if isinstance(val, unjsonnable):
            continue
        if isinstance(val, dict):
            val = json.dumps(val)
        data[key] = val

    url = "https://api.heroku.com/apps/{}/config-vars".format(env_module.HEROKU_APP)
    response = requests.patch(url, auth=('', env_module.HEROKU_API_KEY),
                              headers={"Accept": "application/vnd.heroku+json; version=3"},
                              data=json.dumps(data))
    response.raise_for_status()

    if verbose:
        for key, value in sorted(response.json().items()):
            print('{}: {}'.format(key, value))


@manager.command
def test():
    """Run tests locally"""
    import pytest
    return pytest.main(['-s'])


@manager.command
def livereload():
    from livereload import Server
    server = Server(app)

    # watch all js files else we'll only reload when app.js changes
    paths = pathlib.Path('bauble/static/').glob('**/*.js')
    for f in filter(lambda p: 'vendor' not in p, map(str, paths)):
        server.watch(f)
    server.serve(port=app.config.get('PORT', 5000))


if __name__ == "__main__":
    manager.run()
