import os

from flask import abort, jsonify, render_template, request
from flask.ext.login import login_required
from marshmallow import Schema
from webargs import fields, validate
from webargs.flaskparser import use_args

from bauble.controllers.api import api
import bauble.db as db
from bauble.search import search

root_path, _ = os.path.split(__file__)

class SearchResultSchema(Schema):
    # TODO: pass
    pass

@api.route('/search')
@login_required
@use_args({
    'q': fields.String(required=True, validate=validate.Length(min=1))
})
def get_search(args):
    query = args.get('q', None)
    results = search(query, db.session)

    data = {}
    for key, values in results.items():
        if len(values) > 0:
            data[key] = [obj.jsonify() for obj in values]

    return jsonify(data)
