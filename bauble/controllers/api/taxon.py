import types

import bottle
from bottle import request, response
import sqlalchemy as sa

from bauble import app, API_ROOT
from bauble.middleware import basic_auth, filter_param, build_counts
from bauble.model import Taxon, TaxonDistribution, VernacularName, Geography, get_relation  # TaxonNote


taxon_column_names = [col.name for col in sa.inspect(Taxon).columns]
taxon_mutable = [col for col in taxon_column_names
                 if col not in ['id'] and not col.startswith('_')]

vn_column_names = [col.name for col in sa.inspect(VernacularName).columns]
vn_mutable = [col for col in vn_column_names
              if col not in ['id'] and not col.startswith('_')]

def resolve_taxon(next):
    def _wrapped(*args, **kwargs):
        request.taxon = request.session.query(Taxon).get(request.args['taxon_id'])
        if not request.taxon:
            bottle.abort(404, "Taxon not found")
        return next(*args, **kwargs)
    return _wrapped


def resolve_name(next):
    def _wrapped(*args, **kwargs):
        request.name = request.session.query(VernacularName).get(request.args['name_id'])
        if not request.name:
            bottle.abort(404, "Name not found")
        return next(*args, **kwargs)
    return _wrapped


def build_embedded(embed, taxon):
    if embed == 'synonyms':
        return (embed, [obj.json() for obj in taxon.synonyms])

    data = get_relation(Taxon, taxon.id, embed, session=request.session)
    if isinstance(data, (list, types.GeneratorType)):
        return (embed, [obj.json() for obj in data])
    else:
        return (embed, data.json() if data else {})


@app.get(API_ROOT + "/taxon")
@basic_auth
@filter_param(Taxon, taxon_column_names)
def index_taxon():
    # TODO: we're not doing any sanitization or validation...see preggy or validate.py

    taxa = request.filter if request.filter else request.session.query(Taxon)
    return [taxon.json() for taxon in taxa]


@app.get(API_ROOT + "/taxon/<taxon_id:int>")
@basic_auth
@resolve_taxon
def get_taxon(taxon_id):

    json_data = request.taxon.json()

    if 'embed' in request.params:
        embed_list = request.params.embed if isinstance(request.params.embed, list) \
            else [request.params.embed]
        embedded = map(lambda embed: build_embedded(embed, request.taxon), embed_list)
        json_data.update(embedded)

    return json_data


@app.route(API_ROOT + "/taxon/<taxon_id:int>", method='PATCH')
@basic_auth
@resolve_taxon
def patch_taxon(taxon_id):

    if not request.json:
        bottle.abort(400, 'The request doesn\'t contain a request body')

    # create a copy of the request data with only mutable
    data = {col: request.json[col] for col in request.json.keys()
            if col in taxon_mutable}
    for key, value in data.items():
        setattr(request.taxon, key, data[key])
    request.session.commit()
    return request.taxon.json()


@app.post(API_ROOT + "/taxon")
@basic_auth
def post_taxon():

    if not request.json:
        bottle.abort(400, 'The request doesn\'t contain a request body')

    # create a copy of the request data with only the columns
    data = {col: request.json[col] for col in request.json.keys()
            if col in taxon_mutable}

    # if there isn't a genus_id look for a genus relation on the request data
    if not 'genus_id' in data and 'genus' in request.json and isinstance(request.json['genus'], dict) and 'id' in request.json['genus']:
        data['genus_id'] = request.json['genus']['id']

    # make a copy of the data for only those fields that are columns
    taxon = Taxon(**data)
    request.session.add(taxon)
    request.session.commit()
    response.status = 201
    return taxon.json()


@app.delete(API_ROOT + "/taxon/<taxon_id:int>")
@basic_auth
@resolve_taxon
def delete_taxon(taxon_id):
    request.session.delete(request.taxon)
    request.session.commit()
    response.status = 204


@app.get(API_ROOT + "/taxon/<taxon_id:int>/count")
@basic_auth
@resolve_taxon
@build_counts(Taxon, 'taxon_id')
def count(taxon_id):
    return request.counts


#############################################################
#
# Synonyms routes
#
#############################################################

@app.get(API_ROOT + "/taxon/<taxon_id:int>/synonyms")
@basic_auth
@resolve_taxon
def list_synonyms(taxon_id):
    return request.taxon.synonyms


# @app.get(API_ROOT + "/taxon/<taxon_id:int>/synonyms/<synonym_id:int>")
# @basic_auth
# @resolve_taxon
# def get_synonym(taxon_id, synonym_id):
#     return request.taxon.synonyms


@app.post(API_ROOT + "/taxon/<taxon_id:int>/synonyms")
@basic_auth
@resolve_taxon
def add_synonym(taxon_id):
    synonym_json = request.json
    if 'id' not in synonym_json:
        bottle.abort(400, "No id in request body")
    syn_taxon = request.session.query(Taxon).get(synonym_json['id'])
    request.taxon.synonyms.append(syn_taxon)
    request.session.commit()
    response.status = 201


@app.delete(API_ROOT + "/taxon/<taxon_id:int>/synonyms/<synonym_id:int>")
@basic_auth
@resolve_taxon
def remove_synonym_(taxon_id, synonym_id):
    # synonym_id is the id of the taxon not the TaxonSynonym object
    syn_taxon = request.session.query(Taxon).get(synonym_id)
    request.taxon.synonyms.remove(syn_taxon)
    request.session.commit()
    response.status = 204


#############################################################
#
# Vernacular Names routes
#
#############################################################

@app.get(API_ROOT + "/taxon/<taxon_id:int>/names")
@basic_auth
@resolve_taxon
def list_names(taxon_id):
    return [name.json() for name in request.taxon.vernacular_names]


# @app.get(API_ROOT + "/taxon/<taxon_id:int>/names/<synonym_id:int>")
# @basic_auth
# @resolve_taxon
# def get_synonym(taxon_id, synonym_id):
#     return request.taxon.names


@app.post(API_ROOT + "/taxon/<taxon_id:int>/names")
@basic_auth
@resolve_taxon
def post_name(taxon_id):
    name_json = request.json
    name = VernacularName(name=name_json['name'], language=name_json['language']
                          if 'language' in name_json else None)
    request.taxon.vernacular_names.append(name)
    if 'default' in name_json and name_json['default'] is True:
        request.taxon.default_vernacular_name = name
    request.session.commit()
    response.status = 201
    return name.json()


@app.route(API_ROOT + "/taxon/<taxon_id:int>/names/<name_id:int>", method='PATCH')
@basic_auth
@resolve_taxon
@resolve_name
def patch_name(taxon_id, name_id):

    if not request.json:
        bottle.abort(400, 'The request doesn\'t contain a request body')

    # create a copy of the request data with only the columns
    data = {col: request.json[col] for col in request.json.keys()
            if col in vn_mutable}
    for key, value in data.items():
        setattr(request.name, key, data[key])

    request.session.commit()
    return request.taxon.json()


@app.delete(API_ROOT + "/taxon/<taxon_id:int>/names/<name_id:int>")
@basic_auth
@resolve_taxon
@resolve_name
def remove_name(taxon_id, name_id):
    request.taxon.vernacular_names.remove(request.name)
    request.session.commit()
    response.status = 204


#############################################################
#
# Distribtion routes
#
#############################################################

@app.get(API_ROOT + "/taxon/<taxon_id:int>/distributions")
@basic_auth
@resolve_taxon
def list_distributions(taxon_id):
    return [dist.json() for dist in request.taxon.distribution]


@app.post(API_ROOT + "/taxon/<taxon_id:int>/distributions")
@basic_auth
@resolve_taxon
def post_distribution(taxon_id):
    if 'id' not in request.json:
        bottle.abort(400, "JSON object does not contain a geography id")

    geo_id = request.json['id']
    for dist in request.taxon.distribution:
        # return the dist if it already exists
        if dist.geography_id == geo_id:
            return dist.json()

    # make sure a geo with with id exists
    geo = request.session.query(Geography).get(geo_id)
    if not geo:
        bottle.abort(400, "Unknown geography id")

    dist = TaxonDistribution(geography_id=geo_id)
    request.taxon.distribution.append(dist)
    request.session.commit()
    response.status = 201
    return dist.json()


@app.delete(API_ROOT + "/taxon/<taxon_id:int>/distributions/<geography_id:int>")
@basic_auth
@resolve_taxon
def remove_distribution(taxon_id, geography_id):

    # should we remove all occurrences of this geography only the first??
    for dist in request.taxon.distribution:
        if dist.geography_id == geography_id:
            request.taxon.distribution.remove(dist)

    request.session.commit()
    response.status = 204
