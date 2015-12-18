from flask import jsonify, render_template, request
from flask.ext.login import login_required
from marshmallow import Schema
from webargs import fields, validate
from webargs.flaskparser import use_args
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import Length

import bauble.db as db
from bauble.search import search
from bauble.resource import Resource
import bauble.utils as utils

resource = Resource('search', __name__)


# class SearchForm(Form):
#     q = StringField('q', Length(min=1))


class SearchResultSchema(Schema):
    # TODO: pass
    pass


# TODO: we could probably have a better way map search results to resources....
# maybe even provide a blueprint/resource and use the resource to get the url
# with url_for
result_resource_map = {
    'families': '/family/{}',
    'genera': '/genus/{}',
    'taxa': '/taxon/{}',
    'accessions': '/accession/{}',
    'plants': '/plant/{}',
    'locations': '/location/{}',
    'contacts': '/source/{}'
}


@resource.route('/')
@login_required
@use_args({
    'q': fields.String(validate=validate.Length(min=1))
})
def index(args):
    query = args.get('q', None)
    results = search(query, db.session) if query is not None else {}

    data = {}

    if request.prefers_json:
        for key, values in results.items():
            if len(values) > 0:
                # data[key] = [obj.jsonify() for obj in values]
                data[key] = [obj.jsonify() for obj in values]
        return utils.json_response(jsonify(data))

    for key, values in results.items():
        if len(values) > 0:
            data[key] = [{
                'url': result_resource_map.get(key).format(obj.id),
                'str': obj.str()
            } for obj in values]
    return render_template('search/index.html', results=data)
