from flask.ext.login import login_required
import sqlalchemy.orm as orm
from webargs import fields
from webargs.flaskparser import use_args

from bauble.controllers.api import api
import bauble.db as db
from bauble.models import Family, FamilySynonym
from bauble.helpers import use_model
import bauble.utils as utils

@api.route("/family")
@login_required
def index_family():
    families = Family.query.all()
    data = Family.jsonify(families, many=True)
    return utils.json_response(data)

@api.route("/family/<int:id>")
@login_required
@use_model(Family)
def get_family(family, family_id):
    return utils.json_response(family.jsonify())

@api.route("/family/<int:id>", methods=['PATCH'])
@login_required
@use_model(Family)
def patch_family(family, id):
    db.session.commit()
    return utils.json_response(family.jsonify())

@api.route("/family", methods=['POST'])
@login_required
@use_model(Family)
def post_family(family):
    db.session.add(family)
    db.session.commit()
    return utils.json_response(family.jsonify(), 201)

@api.route("/family/<int:id>", methods=['DELETE'])
@login_required
@use_model(Family)
def delete_family(family, family_id):
    db.session.delete(family)
    db.session.commit()
    return '', 204


@api.route("/family/<int:id>/synonyms", methods=['GET'])
@login_required
def list_family_synonyms(id):
    family = Family.query \
                   .options(orm.joinedload('synonyms')) \
                   .get_or_404(id)
    return FamilySynonym.jsonify(family.synonyms, many=True)


# @api.route("/family/<int:family_id>/synonyms/<int:synonym_id>")
# @login_required
# # @resolve_family
# def get_synonym(family_id, synonym_id):
#     return request.family.synonyms


# @api.route("/family/<int:family_id>/synonyms", methods=['POST'])
# @login_required
# @use_args({

# })
# def add_synonym(args, family_id):
#     family = Family.query.get_or_404(family_id)

#     # TODO: not finished

#     synonym_json = request.json
#     if 'id' not in synonym_json:
#         abort(400, "No id in request body")

#     syn_family = db.session.query(Family).get(synonym_json['id'])
#     if not syn_family:
#         abort(422, 'Invalid family id for synonym')

#     request.family.synonyms.append(syn_family)
#     db.session.commit()
#     return '', 201


@api.route("/family/<int:id>/synonyms/<int:synonym_id>", methods=['DELETE'])
@use_model(Family)
@login_required
def remove_family_synonym(family, family_id, synonym_id):
    syn_family = Family.query.get_or_404(synonym_id)
    family.synonyms.remove(syn_family)
    db.session.commit()
    return '', 204


@api.route("/family/<int:family_id>/count")
@login_required
@use_args({
    'relation': fields.DelimitedList(fields.String(), required=True)
})
def family_count(args, family_id):
    data = {}
    family = Family.query.get_or_404(family_id)
    for relation in args['relation']:
        _, base = relation.rsplit('/', 1)
        data[base] = utils.count_relation(family, relation)
    return utils.json_response(data)
