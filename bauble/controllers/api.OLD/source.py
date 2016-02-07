from flask.ext.login import login_required

from bauble.controllers.api import api
import bauble.db as db
from bauble.models import SourceDetail
from bauble.middleware import use_model
import bauble.utils as utils

@api.route("/source")
@login_required
def index_source():
    sources = SourceDetail.query.all()
    data = SourceDetail.jsonify(sources, many=True)
    return utils.json_response(data)


@api.route("/source/<int:id>")
@login_required
@use_model(SourceDetail)
def get_source(source_detail, id):
    return utils.json_response(source_detail.jsonify())


@api.route("/source/<int:id>", methods=['PATCH'])
@login_required
@use_model(SourceDetail)
def patch_source(source_detail, id):
    db.session.commit()
    return utils.json_response(source_detail.jsonify())


@api.route("/source", methods=['POST'])
@login_required
@use_model(SourceDetail)
def post_source(source_detail):
    db.session.add(source_detail)
    db.session.commit()
    return utils.json_response(source_detail.jsonify(), 201)


@api.route("/source/<int:id>", methods=['DELETE'])
@login_required
@use_model(SourceDetail)
def delete_source_detail(source_detail, source_detail_id):
    db.session.delete(source_detail)
    db.session.commit()
    return '', 204
