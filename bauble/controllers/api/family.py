from flask import abort, request
from flask.ext.login import login_required
import sqlalchemy.orm as orm
from webargs import fields
from webargs.flaskparser import use_args

from bauble.controllers.api import api
import bauble.db as db
from bauble.models import Family, FamilySynonym
import bauble.utils as utils

@api.route("/family")
@login_required
def index_family():
    families = Family.query.all()
    data = Family.jsonify(families, many=True)
    return utils.json_response(data)


@api.route("/family/<int:family_id>")
@login_required
def get_family(family_id):
    family = Family.query.get_or_404(family_id)
    return utils.json_response(family.jsonify())


@api.route("/family/<int:family_id>", methods=['PATCH'])
@login_required
@use_args({
    'family': fields.String()
})
def patch_family(args, family_id):
    family = Family.query.get_or_404(family_id)
    for key, value in args.items():
        setattr(family, key, value)
    db.session.commit()
    return utils.json_response(family.jsonify())


@api.route("/family", methods=['POST'])
@login_required
@use_args({
    'family': fields.String()
})
def post_family(args):
    family = Family(**args)
    db.session.add(family)
    db.session.commit()
    return utils.json_response(family.jsonify(), 201)


@api.route("/family/<int:family_id>", methods=['DELETE'])
@login_required
def delete_family(family_id):
    family = Family.query.get_or_404(family_id)
    db.session.delete(family)
    db.session.commit()
    return '', 204


@api.route("/family/<int:family_id>/synonyms", methods=['GET'])
@login_required
def list_synonyms(family_id):
    family = Family.query \
                   .options(orm.joinedload('synonyms')) \
                   .get_or_404(family_id)
    return FamilySynonym.jsonify(family.synonyms, many=True)


# @api.route("/family/<int:family_id>/synonyms/<int:synonym_id>")
# @login_required
# # @resolve_family
# def get_synonym(family_id, synonym_id):
#     return request.family.synonyms


@api.route("/family/<int:family_id>/synonyms", methods=['POST'])
@login_required
@use_args({

})
def add_synonym(args, family_id):
    synonym_json = request.json
    if 'id' not in synonym_json:
        abort(400, "No id in request body")
    syn_family = db.session.query(Family).get(synonym_json['id'])
    request.family.synonyms.append(syn_family)
    db.session.commit()
    return '', 201


@api.route("/family/<int:family_id>/synonyms/<int:synonym_id>", methods=['DELETE'])
@login_required
def remove_synonym(family_id, synonym_id):
    family = Family.query.get_or_404(family_id)
    syn_family = Family.query.get_or_404(synonym_id)
    family.synonyms.remove(syn_family)
    db.session.commit()
    return '', 204



@api.route("/family/<int:family_id>/count")
@login_required
@use_args({
    'relation': fields.DelimitedList(fields.String(), required=True)
})
def count(args, family_id):
    data = {}
    family = Family.query.get_or_404(family_id)
    for relation in args['relation']:
        _, base = relation.rsplit('/', 1)
        data[base] = utils.count_relation(family, relation)
    return utils.json_response(data)
