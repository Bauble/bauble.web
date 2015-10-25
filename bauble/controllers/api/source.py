
import bottle
from bottle import request, response
import sqlalchemy as sa

from bauble import app, API_ROOT
from bauble.middleware import basic_auth, filter_param
from bauble.model import SourceDetail

column_names = [col.name for col in sa.inspect(SourceDetail).columns]

def resolve_source(next):
    def _wrapped(*args, **kwargs):
        request.source = request.session.query(SourceDetail).get(request.args['source_id'])
        if not request.source:
            bottle.abort(404, "Source not found")
        return next(*args, **kwargs)
    return _wrapped


@app.get(API_ROOT + "/source")
@basic_auth
@filter_param(SourceDetail, column_names)
def index_source():
    # TODO: we're not doing any sanitization or validation...see preggy or validate.py

    sources = request.filter if request.filter else request.session.query(SourceDetail)
    return [source.json() for source in sources]


@app.get(API_ROOT + "/source/<source_id:int>")
@basic_auth
@resolve_source
def get_source(source_id):
    return request.source.json()


@app.route(API_ROOT + "/source/<source_id:int>", method='PATCH')
@basic_auth
@resolve_source
def patch_source(source_id):

    if not request.json:
        bottle.abort(400, 'The request doesn\'t contain a request body')

    # create a copy of the request data with only the columns
    data = {col: request.json[col] for col in request.json.keys() if col in column_names}
    for key, value in data.items():
        setattr(request.source, key, data[key])
    request.session.commit()
    return request.source.json()


@app.post(API_ROOT + "/source")
@basic_auth
def post_source():

    # TODO create a subset of the columns that we consider mutable
    mutable = []

    # create a copy of the request data with only the columns
    data = {col: request.json[col] for col in request.json.keys() if col in column_names}

    # make a copy of the data for only those fields that are columns
    source = SourceDetail(**data)
    request.session.add(source)
    request.session.commit()
    response.status = 201
    return source.json()


@app.delete(API_ROOT + "/source/<source_id:int>")
@basic_auth
@resolve_source
def delete_source(source_id):
    request.session.delete(request.source)
    request.session.commit()
    response.status = 204
