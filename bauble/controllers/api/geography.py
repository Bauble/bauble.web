
import bottle
from bottle import request

from bauble import app, API_ROOT
from bauble.middleware import basic_auth
from bauble.model import Geography


@app.get(API_ROOT + "/geographies")
@basic_auth
def list_geography():
    return [geo.json() for geo in request.session.query(Geography)]


@app.get(API_ROOT + "/geographies/<geography_id:int>")
@basic_auth
def get_geography(geography_id):
    geography = request.session.query(Geography).get(geography_id)
    if not geography:
        bottle.abort(404, "Geography not found")
    return geography.json()
