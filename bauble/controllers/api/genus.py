from flask import abort
from flask.ext.login import login_required
import sqlalchemy.orm as orm
from webargs import fields
from webargs.flaskparser import use_args

from bauble.controllers.api import api
import bauble.db as db
from bauble.models import Genus, GenusNote, GenusSynonym, Family
import bauble.utils as utils

@api.route("/genus")
@login_required
def index_genus():
    genera = Genus.query.all()
    data = Genus.jsonify(genera, many=True)
    return utils.json_response(data)


@api.route("/genus/<int:genus_id>")
@login_required
def get_genus(genus_id):
    genus = Genus.query.get_or_404(genus_id)
    return utils.json_response(genus.jsonify())


@api.route("/genus/<int:genus_id>", methods=['PATCH'])
@login_required
@use_args({
    'family_id': fields.Int(),
    'genus': fields.String()
})
def patch_genus(args, genus_id):
    genus = Genus.query.get_or_404(genus_id)
    for key, value in args.items():
        setattr(genus, key, value)
    db.session.commit()
    return utils.json_response(genus.jsonify())


@api.route("/genus", methods=['POST'])
@login_required
@use_args({
    'genus': fields.String(),
    'family_id': fields.Int(required=True)
})
def post_genus(args):
    family = Family.query.filter_by(id=args['family_id']).first()
    if not family:
        abort(422, "Invalid family id")

    genus = Genus(**args)
    db.session.add(genus)
    db.session.commit()
    return utils.json_response(genus.jsonify(), 201)


@api.route("/genus/<int:genus_id>", methods=['DELETE'])
@login_required
def delete_genus(genus_id):
    genus = Genus.query.get_or_404(genus_id)
    db.session.delete(genus)
    db.session.commit()
    return '', 204


@api.route("/genus/<int:genus_id>/synonyms")
@login_required
def list_genus_synonyms(genus_id):
    genus = Genus.query \
                 .options(orm.joinedload('synonyms')) \
                 .get_or_404(genus_id)
    return GenusSynonym.jsonify(genus.synonyms, many=True)


# @api.get("/genus/<int:genus_id>/synonyms/<synonym_id:int>")
# @login_required
# # def get_synonym(genus_id, synonym_id):
#     return request.genus.synonyms


# @api.post("/genus/<int:genus_id>/synonyms")
# @login_required
# def add_synonym(genus_id):
#     synonym_json = request.json
#     if 'id' not in synonym_json:
#         bottle.abort(400, "No id in request body")
#     syn_genus = request.session.query(Genus).get(synonym_json['id'])
#     request.genus.synonyms.append(syn_genus)
#     request.session.commit()
#     response.status = 201


@api.route("/genus/<int:genus_id>/synonyms/<int:synonym_id>", methods=['DELETE'])
@login_required
def remove_genus_synonym(genus_id, synonym_id):
    genus = Genus.query.get_or_404(genus_id)
    syn_genus = Genus.query.get_or_404(synonym_id)
    genus.synonyms.remove(syn_genus)
    db.session.commit()
    return '', 204


@api.route("/genus/<int:genus_id>/count")
@login_required
@use_args({
    'relation': fields.DelimitedList(fields.String(), required=True)
})
def genus_count(args, genus_id):
    data = {}
    genus = Genus.query.get_or_404(genus_id)
    for relation in args['relation']:
        _, base = relation.rsplit('/', 1)
        data[base] = utils.count_relation(genus, relation)
    return utils.json_response(data)
