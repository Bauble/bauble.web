from flask import abort
from flask.ext.login import login_required
import sqlalchemy.orm as orm
from webargs import fields
from webargs.flaskparser import use_args

from bauble.controllers.api import api
import bauble.db as db
from bauble.models import Taxon, TaxonNote, TaxonSynonym, Genus
import bauble.utils as utils

@api.route("/taxon")
@login_required
def index_taxon():
    genera = Taxon.query.all()
    data = Taxon.jsonify(genera, many=True)
    return utils.json_response(data)


@api.route("/taxon/<int:taxon_id>")
@login_required
def get_taxon(taxon_id):
    taxon = Taxon.query.get_or_404(taxon_id)
    return utils.json_response(taxon.jsonify())


@api.route("/taxon/<int:taxon_id>", methods=['PATCH'])
@login_required
@use_args({
    'sp': fields.String()
})
def patch_taxon(args, taxon_id):
    taxon = Taxon.query.get_or_404(taxon_id)
    for key, value in args.items():
        setattr(taxon, key, value)
    db.session.commit()
    return utils.json_response(taxon.jsonify())


@api.route("/taxon", methods=['POST'])
@login_required
@use_args({
    'sp': fields.String(),
    'genus_id': fields.Int(required=True)
})
def post_taxon(args):
    genus = Genus.query.filter_by(id=args['genus_id']).first()
    if not genus:
        abort(422, "Invalid genus id")

    taxon = Taxon(**args)
    db.session.add(taxon)
    db.session.commit()
    return utils.json_response(taxon.jsonify(), 201)


@api.route("/taxon/<int:taxon_id>", methods=['DELETE'])
@login_required
def delete_taxon(taxon_id):
    taxon = Taxon.query.get_or_404(taxon_id)
    db.session.delete(taxon)
    db.session.commit()
    return '', 204


@api.route("/taxon/<int:taxon_id>/count")
@login_required
@use_args({
    'relation': fields.DelimitedList(fields.String(), required=True)
})
def taxon_count(args, taxon_id):
    data = {}
    taxon = Taxon.query.get_or_404(taxon_id)
    for relation in args['relation']:
        _, base = relation.rsplit('/', 1)
        data[base] = utils.count_relation(taxon, relation)
    return utils.json_response(data)

#
# Synonym routes
#


@api.route("/taxon/<int:taxon_id>/synonyms")
@login_required
def list_taxon_synonyms(taxon_id):
    taxon = Taxon.query \
                 .options(orm.joinedload('synonyms')) \
                 .get_or_404(taxon_id)
    return TaxonSynonym.jsonify(taxon.synonyms, many=True)


# @api.route("/taxon/<int:taxon_id>/synonyms/<synonym_id:int>")
# @login_required
# # def get_synonym(taxon_id, synonym_id):
#     return request.taxon.synonyms


# @api.post("/taxon/<int:taxon_id>/synonyms")
# @login_required
# def add_synonym(taxon_id):
#     synonym_json = request.json
#     if 'id' not in synonym_json:
#         bottle.abort(400, "No id in request body")
#     syn_taxon = request.session.query(Taxon).get(synonym_json['id'])
#     request.taxon.synonyms.append(syn_taxon)
#     request.session.commit()
#     response.status = 201


@api.route("/taxon/<int:taxon_id>/synonyms/<int:synonym_id>", methods=['DELETE'])
@login_required
def remove_taxon_synonym(taxon_id, synonym_id):
    taxon = Taxon.query.get_or_404(taxon_id)
    syn_taxon = Taxon.query.get_or_404(synonym_id)
    taxon.synonyms.remove(syn_taxon)
    db.session.commit()
    return '', 204

#
# Vernacular Names routes
#

@api.route("/taxon/<int:taxon_id>/names")
@login_required
def list_names(taxon_id):
    taxon = Taxon.query.get_or_404(taxon_id)
    return [name.json() for name in taxon.vernacular_names]


# @api.post("/taxon/<int:taxon_id>/names")
# @login_required
# def post_name(taxon_id):
#     name_json = request.json
#     name = VernacularName(name=name_json['name'], language=name_json['language']
#                           if 'language' in name_json else None)
#     request.taxon.vernacular_names.append(name)
#     if 'default' in name_json and name_json['default'] is True:
#         request.taxon.default_vernacular_name = name
#     request.session.commit()
#     response.status = 201
#     return name.json()


# @api.route("/taxon/<int:taxon_id>/names/<name_id:int>", method='PATCH')
# @login_required
# @resolve_name
# def patch_name(taxon_id, name_id):

#     if not request.json:
#         bottle.abort(400, 'The request doesn\'t contain a request body')

#     # create a copy of the request data with only the columns
#     data = {col: request.json[col] for col in request.json.keys()
#             if col in vn_mutable}
#     for key, value in data.items():
#         setattr(request.name, key, data[key])

#     request.session.commit()
#     return request.taxon.json()


# @api.delete("/taxon/<int:taxon_id>/names/<name_id:int>")
# @login_required
# @resolve_name
# def remove_name(taxon_id, name_id):
#     request.taxon.vernacular_names.remove(request.name)
#     request.session.commit()
#     response.status = 204


#############################################################
#
# Distribtion routes
#
#############################################################

@api.route("/taxon/<int:taxon_id>/distributions")
@login_required
def list_distributions(taxon_id):
    return [dist.json() for dist in request.taxon.distribution]


@api.route("/taxon/<int:taxon_id>/distributions", methods=['POST'])
@login_required
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


@api.route("/taxon/<int:taxon_id>/distributions/<int:geography_id>", methods=['DELETE'])
@login_required
def remove_distribution(taxon_id, geography_id):

    # should we remove all occurrences of this geography only the first??
    for dist in request.taxon.distribution:
        if dist.geography_id == geography_id:
            request.taxon.distribution.remove(dist)

    request.session.commit()
    response.status = 204
