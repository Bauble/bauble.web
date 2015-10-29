from flask.ext.login import login_required
from webargs import fields
from webargs.flaskparser import use_args

from bauble.controllers.api import api
import bauble.db as db
from bauble.models import Location
import bauble.utils as utils


@api.route("/location")
@login_required
def index_location():
    locations = Location.query.all()
    data = Location.jsonify(locations, many=True)
    return utils.json_response(data)


@api.route("/location/<int:location_id>")
@login_required
def get_location(location_id):
    location = Location.query.get_or_404(location_id)
    return utils.json_response(location.jsonify())


@api.route("/location/<int:location_id>", methods=['PATCH'])
@use_args({
    'code': fields.String(),
    'name': fields.String(),
    'description': fields.String()
})
def patch_location(args, location_id):
    location = Location.query.get_or_404(location_id)
    for key, value in args.items():
        setattr(location, key, value)
    db.session.commit()
    return utils.json_response(location.jsonify())


@api.route("/location", methods=['POST'])
@login_required
@use_args({
    'code': fields.String(required=True),
    'name': fields.String(),
    'description': fields.String()
})
def post_location(args):
    location = Location(**args)
    db.session.add(location)
    db.session.commit()
    return utils.json_response(location.jsonify(), 201)


@api.route("/location/<int:location_id>", methods=['DELETE'])
@login_required
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    return '', 204


@api.route("/location/<int:location_id>/count")
@login_required
@use_args({
    'relation': fields.DelimitedList(fields.String(), required=True)
})
def location_count(args, location_id):
    data = {}
    location = Location.query.get_or_404(location_id)
    for relation in args['relation']:
        _, base = relation.rsplit('/', 1)
        data[base] = utils.count_relation(location, relation)
    return utils.json_response(data)
