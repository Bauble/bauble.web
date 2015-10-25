
import bottle
from bottle import request, response
import sqlalchemy as sa

from bauble import app, API_ROOT
from bauble.middleware import basic_auth, build_counts, filter_param, resolve_relation
from bauble.model import Accession, Source, Collection, Propagation, PropSeed, PropCutting, get_relation

acc_column_names = [col.name for col in sa.inspect(Accession).columns]
acc_mutable = [col for col in acc_column_names
               if col not in ['id'] and not col.startswith('_')]

source_mutable = ['sources_code', 'id', 'plant_propagation_id']

prop_seed_mutable = [col.name for col in sa.inspect(PropSeed).columns
                     if col.name not in ['id']]
prop_cutting_mutable = [col.name for col in sa.inspect(PropCutting).columns
                        if col.name not in ['id']]

coll_mutable = [col.name for col in sa.inspect(Collection).columns
                if col.name not in ['id']]

def resolve_accession(next):
    def _wrapped(*args, **kwargs):
        request.accession = request.session.query(Accession).get(request.args['accession_id'])
        if not request.accession:
            bottle.abort(404, "Accession not found")
        return next(*args, **kwargs)
    return _wrapped


def resolve_source(next):
    def _wrapped(*args, **kwargs):
        request.source = request.session.query(Source).get(request.args['source_id'])
        if not request.source:
            bottle.abort(404, "Source not found")
        return next(*args, **kwargs)
    return _wrapped


def build_embedded(embed, accession):
    data = get_relation(Accession, accession.id, embed, session=request.session)

    if isinstance(data, list):
        return (embed, [obj.json() for obj in data])
    else:
        return (embed, data.json() if data else {})


@app.get(API_ROOT + "/accession")
@basic_auth
@filter_param(Accession, acc_column_names)
def index_accession():
    # TODO: we're not doing any sanitization or validation...see preggy or validate.py

    accessions = request.filter if request.filter else request.session.query(Accession)
    return [accession.json() for accession in accessions]


@app.get(API_ROOT + "/accession/<accession_id:int>")
@basic_auth
@resolve_accession
def get_accession(accession_id):

    json_data = request.accession.json()

    if 'embed' in request.params:
        embed_list = request.params.embed if isinstance(request.params.embed, list) \
            else [request.params.embed]
        embedded = map(lambda embed: build_embedded(embed, request.accession), embed_list)
        json_data.update(embedded)

    return json_data


@app.route(API_ROOT + "/accession/<accession_id:int>", method='PATCH')
@basic_auth
@resolve_accession
def patch_accession(accession_id):

    if not request.json:
        bottle.abort(400, 'The request doesn\'t contain a request body')

    # create a copy of the request data with only the columns
    data = {col: request.json[col] for col in request.json.keys()
            if col in acc_mutable}
    request.accession.set_attributes(data)

    if 'source' in request.json:
        if request.accession.source is None:
            request.accession.source = Source()
        source = request.accession.source  # shorthand

        source_json = request.json['source']
        source_data = {col: source_json[col] for col in source_json.keys()
                       if col in source_mutable}
        source_data['source_detail_id'] = source_data.pop('id', None)

        # make a copy of the data for only those fields that are columns
        source.set_attributes(source_data)

        # make sure the propagation type is not empty b/c we'll get an error
        # trying to set the propagation details (even if it's an empty dict) if
        # the prop_type hasn't been set
        if 'propagation' in source_json and len(source_json['propagation']) > 0:
            # TODO: validate prop_type
            if source.propagation is None:
                source.propagation = Propagation()

            prop_data = source_json['propagation']
            source.propagation.prop_type = prop_data.pop('prop_type', source.propagation.prop_type)
            prop_mutable = prop_seed_mutable if source.propagation.prop_type == 'Seed' \
                else prop_cutting_mutable
            source.propagation.details = {col: prop_data[col] for col in prop_data.keys()
                                          if col in prop_mutable}

        if 'collection' in source_json and len(source_json['collection']) > 0:
            # TODO: validate collection datand set mutable properties
            if source.collection is None:
                source.collection = Collection()
            coll_data = {col: value for col, value in source_json['collection'].items()
                         if col in coll_mutable}
            source.collection.set_attributes(coll_data)


    request.session.commit()
    return request.accession.json()


@app.post(API_ROOT + "/accession")
@basic_auth
@resolve_relation('taxon_id', 'taxon')
def post_accession():

    # create a copy of the request data with only the columns
    data = {col: request.json[col] for col in request.json.keys()
            if col in acc_mutable}

    # make a copy of the data for only those fields that are columns
    accession = Accession(**data)
    request.session.add(accession)

    if 'source' in request.json:
        source_json = request.json['source']
        source_data = {col: source_json[col] for col in source_json.keys()
                       if col in source_mutable}
        source_data['source_detail_id'] = source_data.pop('id', None)

        # make a copy of the data for only those fields that are columns
        source = Source(**source_data)
        request.session.add(source)

        if 'propagation' in source_json:
            # TODO: validate prop_type
            prop_data = source_json['propagation']
            propagation = Propagation(prop_type=prop_data.pop('prop_type'))
            prop_mutable = prop_seed_mutable if propagation.prop_type == 'Seed' \
                else prop_cutting_mutable

            propagation.details = {col: prop_data[col] for col in prop_data.keys()
                                   if col in prop_mutable}
            source.propagation = propagation


        collection = Collection()
        if 'collection' in source_json:
            # TODO: validate collection datand set mutable properties
            coll_data = {col: value for col, value in source_json['collection'].items()
                         if col in coll_mutable}
            collection = Collection(**coll_data)
            source.collection = collection


    request.session.commit()
    response.status = 201
    return accession.json()


@app.delete(API_ROOT + "/accession/<accession_id:int>")
@basic_auth
@resolve_accession
def delete_accession(accession_id):
    request.session.delete(request.accession)
    request.session.commit()
    response.status = 204


@app.get(API_ROOT + "/accession/<accession_id:int>/count")
@basic_auth
@resolve_accession
@build_counts(Accession, 'accession_id')
def count(accession_id):
    return request.counts
