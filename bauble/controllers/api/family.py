from flask import abort, request
from flask.ext.login import login_required
import sqlalchemy as sa

from bauble.controllers.api import api
# import bauble.db as db

# from bauble.middleware import basic_auth, filter_param, build_counts
from bauble.models import Family  # , get_relation
import bauble.utils as utils

family_column_names = [col.name for col in sa.inspect(Family).columns]
family_mutable = [col for col in family_column_names
                  if col not in ['id'] and not col.startswith('_')]

def resolve_family(next):
    def _wrapped(*args, **kwargs):
        request.family = request.session.query(Family).get(request.args['family_id'])
        if not request.family:
            abort(404, "Family not found")
        return next(*args, **kwargs)
    return _wrapped


@api.route("/family")
@login_required
def index_family():
    families = Family.query.all()
    data = Family.jsonify(families, many=True)
    return utils.json_response(data)


@api.route("/family/<int:family_id>")
@login_required
def get_family(family_id):
    return
    json_data = request.family.json()

    # if 'embed' in request.params:
    #     embed_list = request.params.embed if isinstance(request.params.embed, list) \
    #         else [request.params.embed]
    #     embedded = map(lambda embed: build_embedded(embed, request.family), embed_list)
    #     json_data.update(embedded)

    return json_data


@api.route("/family/<int:family_id>", methods=['PATCH'])
@login_required
# @resolve_family
def patch_family(family_id):

    if not request.json:
        abort(400, 'The request doesn\'t contain a request body')

    # TODO: restrict the columns to only those that are patchable which might be different
    # than the columns that a postable

    # create a copy of the request data with only the columns that are mutable
    data = {col: request.json[col] for col in request.json.keys()
            if col in family_mutable}
    for key, value in data.items():
        setattr(request.family, key, data[key])
    request.session.commit()

    return request.family.json()


@api.route("/family", methods=['POST'])
@login_required
def post_family():

    if not request.json:
        abort(400, 'The request doesn\'t contain a request body')

    # create a copy of the request data with only the mutable columns
    data = {col: request.json[col] for col in request.json.keys()
            if col in family_mutable}

    family = Family(**data)
    request.session.add(family)
    request.session.commit()
    return family.jsonify(), 201


@api.route("/family/<int:family_id>", methods=['DELETE'])
@login_required
# @resolve_family
def delete_family(family_id):
    request.session.delete(request.family)
    request.session.commit()
    return '', 204


@api.route("/family/<int:family_id>/synonyms", methods=['GET'])
@login_required
# @resolve_family
def list_synonyms(family_id):
    return request.family.synonyms


@api.route("/family/<int:family_id>/synonyms/<int:synonym_id>")
@login_required
# @resolve_family
def get_synonym(family_id, synonym_id):
    return request.family.synonyms


@api.route("/family/<int:family_id>/synonyms", methods=['POST'])
@login_required
# @resolve_family
def add_synonym(family_id):
    synonym_json = request.json
    if 'id' not in synonym_json:
        abort(400, "No id in request body")
    syn_family = request.session.query(Family).get(synonym_json['id'])
    request.family.synonyms.append(syn_family)
    request.session.commit()
    return '', 201


@api.route("/family/<int:family_id>/synonyms/<int:synonym_id>", methods=['DELETE'])
@login_required
# @resolve_family
def remove_synonym(family_id, synonym_id):
    # synonym_id is the id of the family not the FamilySynonym object
    syn_family = request.session.query(Family).get(synonym_id)
    request.family.synonyms.remove(syn_family)
    request.session.commit()
    return '', 204



@api.route("/family/<int:family_id>/count")
@login_required
# @resolve_family
# @build_counts(Family, 'family_id')
def count(family_id):
    return request.counts
