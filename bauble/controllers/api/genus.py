import types

import bottle
from bottle import request, response
import sqlalchemy as sa

from bauble import app, API_ROOT
from bauble.middleware import basic_auth, build_counts, filter_param
from bauble.model import Genus, get_relation  # , GenusNote, GenusSynonym

genus_column_names = [col.name for col in sa.inspect(Genus).columns]
genus_mutable = [col for col in genus_column_names
                 if col not in ['id'] and not col.startswith('_')]


def resolve_genus(next):
    def _wrapped(*args, **kwargs):
        request.genus = request.session.query(Genus).get(request.args['genus_id'])
        if not request.genus:
            bottle.abort(404, "Genus not found")
        return next(*args, **kwargs)
    return _wrapped


def build_embedded(embed, genus):
    if embed == 'synonyms':
        # handle synonyms differently since they're an SA association list
        return (embed, [obj.json() for obj in genus.synonyms])

    data = get_relation(Genus, genus.id, embed, session=request.session)
    if isinstance(data, (list, types.GeneratorType)):
        return (embed, [obj.json() for obj in data])
    else:
        return (embed, data.json() if data else {})



@app.get(API_ROOT + "/genus")
@basic_auth
@filter_param(Genus, genus_column_names)
def index_genus():
    # TODO: we're not doing any sanitization or validation...see preggy or validate.py
    genera = request.filter if request.filter else request.session.query(Genus)
    return [genus.json() for genus in genera]


@app.get(API_ROOT + "/genus/<genus_id:int>")
@basic_auth
@resolve_genus
def get_genus(genus_id):
    json_data = request.genus.json()

    if 'embed' in request.params:
        embed_list = request.params.embed if isinstance(request.params.embed, list) \
            else [request.params.embed]
        embedded = map(lambda embed: build_embedded(embed, request.genus), embed_list)
        json_data.update(embedded)

    return json_data


@app.route(API_ROOT + "/genus/<genus_id:int>", method='PATCH')
@basic_auth
@resolve_genus
def patch_genus(genus_id):

    if not request.json:
        bottle.abort(400, 'The request doesn\'t contain a request body')

    # create a copy of the request data with only the columns
    data = {col: request.json[col] for col in request.json.keys()
            if col in genus_mutable}
    for key, value in data.items():
        setattr(request.genus, key, data[key])
    request.session.commit()
    return request.genus.json()


@app.post(API_ROOT + "/genus")
@basic_auth
def post_genus():

    if not request.json:
        bottle.abort(400, 'The request doesn\'t contain a request body')

    # create a copy of the request data with only the columns
    data = {col: request.json[col] for col in request.json.keys()
            if col in genus_mutable}

    # if there isn't a family_id look for a family relation on the request data
    if not 'family_id' in data and 'family' in request.json and isinstance(request.json['family'], dict) and 'id' in request.json['family']:
        data['family_id'] = request.json['family']['id']

    # make a copy of the data for only those fields that are columns
    genus = Genus(**data)
    request.session.add(genus)
    request.session.commit()
    response.status = 201
    return genus.json()


@app.delete(API_ROOT + "/genus/<genus_id:int>")
@basic_auth
@resolve_genus
def delete_genus(genus_id):
    request.session.delete(request.genus)
    request.session.commit()
    response.status = 204


@app.get(API_ROOT + "/genus/<genus_id:int>/synonyms")
@basic_auth
@resolve_genus
def list_synonyms(genus_id):
    return request.genus.synonyms


# @app.get(API_ROOT + "/genus/<genus_id:int>/synonyms/<synonym_id:int>")
# @basic_auth
# @resolve_genus
# def get_synonym(genus_id, synonym_id):
#     return request.genus.synonyms


@app.post(API_ROOT + "/genus/<genus_id:int>/synonyms")
@basic_auth
@resolve_genus
def add_synonym(genus_id):
    synonym_json = request.json
    if 'id' not in synonym_json:
        bottle.abort(400, "No id in request body")
    syn_genus = request.session.query(Genus).get(synonym_json['id'])
    request.genus.synonyms.append(syn_genus)
    request.session.commit()
    response.status = 201


@app.delete(API_ROOT + "/genus/<genus_id:int>/synonyms/<synonym_id:int>")
@basic_auth
@resolve_genus
def remove_synonym_(genus_id, synonym_id):
    # synonym_id is the id of the genus not the GenusSynonym object
    syn_genus = request.session.query(Genus).get(synonym_id)
    request.genus.synonyms.remove(syn_genus)
    request.session.commit()
    response.status = 204


@app.get(API_ROOT + "/genus/<genus_id:int>/count")
@basic_auth
@resolve_genus
@build_counts(Genus, 'genus_id')
def count(genus_id):
    return request.counts
