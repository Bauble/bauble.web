
import json

import bottle
from bottle import request, response
import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.exc as sa_exc

from bauble import app, API_ROOT
import bauble.db as db
import bauble.mimetype as mimetype
from bauble.middleware import basic_auth, accept
from bauble.model import User
from bauble.routes import auth

user_column_names = [col.name for col in sa.inspect(User).columns]
user_mutable = [col for col in user_column_names
                if col not in ['id', 'access_token', 'access_token_expiration']
                and not col.startswith('_')]

def resolve_user(next):
    def _wrapped(*args, **kwargs):
        request.user = request.session.query(User).get(request.args['user_id'])
        return next(*args, **kwargs)
    return _wrapped


#
# TODO: This should be an admin only route.  Temporarily disable it for now.
#
#@app.get(API_ROOT + "/user")
#@basic_auth
def index_user():
    # TODO: we're not doing any sanitization or validation...see preggy or validate.py
    orgs = request.session.query(User)
    q = request.query.q
    if q:
        # TODO: this should be a ilike or something simiar
        orgs = orgs.filter_by(username=q)

    # set response type explicitly since the auto json doesn't trigger for
    # lists for some reason
    response.content_type = '; '.join((mimetype.json, "charset=utf8"))
    return json.dumps([user.json() for user in orgs])


@app.get(API_ROOT + "/user/<user_id:int>")
@basic_auth
@accept(mimetype.json)
@resolve_user
def get_user(user_id):
    return request.user.json()


@app.route(API_ROOT + "/user/<user_id:int>", method='PATCH')
@basic_auth
@resolve_user
def patch_user(user_id):

    # create a copy of the request data with only the columns
    data = {col: request.json[col] for col in request.json.keys()
            if col in user_mutable}
    for key, value in data.items():
        setattr(request.user, key, data[key])
    request.session.commit()
    return request.user.json()


@app.post(API_ROOT + "/user")
def post_user():
    """
    Create a new user.
    """
    # TODO: send an email to verify user account

    # create a copy of the request data with only the columns
    data = {col: request.json[col] for col in request.json.keys()
            if col in user_mutable}

    session = db.Session()
    try:
        user = User(**data)
        user.access_token, user.access_token_expiration = auth.create_access_token()
        session.add(user)
        session.commit()
        response.status = 201
        return user.json()
    except sa_exc.IntegrityError as exc:
        print('exc.orig.diag.column_name,: ', exc.orig.diag.column_name,)
        bottle.abort(409, exc)
    finally:
        session.close()


@app.delete(API_ROOT + "/user/<user_id:int>")
@basic_auth
@resolve_user
def delete_user(user_id):
    request.session.delete(request.user)
    request.session.commit()
    response.status = 204


@app.get(API_ROOT + "/user/<user_id:int>/<relations:path>")
@basic_auth
@resolve_user
def get_user_relation(user_id, relations):

    mapper = orm.class_mapper(User)
    for name in relations.split('/'):
        mapper = getattr(mapper.relationships, name).mapper

    query = request.session.query(User, mapper.class_)\
        .filter(getattr(User, 'id') == user_id)\
        .join(*relations.split('/'))

    response.content_type = '; '.join((mimetype.json, "charset=utf8"))
    return json.dumps([obj.json() for parent, obj in query])
