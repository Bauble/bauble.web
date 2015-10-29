from flask import abort
from flask.ext.login import login_required
from webargs import fields
from webargs.flaskparser import use_args

from bauble.controllers.api import api
import bauble.db as db
from bauble.models import Accession, Location, Plant
import bauble.utils as utils


@api.route("/plant")
@login_required
def index_plant():
    plants = Plant.query.all()
    data = Plant.jsonify(plants, many=True)
    return utils.json_response(data)


@api.route("/plant/<int:plant_id>")
@login_required
def get_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    return utils.json_response(plant.jsonify())


@api.route("/plant/<int:plant_id>", methods=['PATCH'])
@use_args({
    'accession_id': fields.Int(),
    'location_id': fields.Int(),
    'code': fields.String()
})
def patch_plant(args, plant_id):
    if 'location_id' in args:
        location = Location.query.filter_by(id=args['location_id']).first()
        if not location:
            abort(422, "Invalid location id")

    if 'accession_id' in args:
        accession = Accession.query.filter_by(id=args['accession_id']).first()
        if not accession:
            abort(422, "Invalid session id")

    # create the plant change
    # change = PlantChange(plant_id=request.plant.id,
    #                      from_location_id=request.plant.location_id,
    #                      quantity=request.plant.quantity,  # store original quantity
    #                      person=request.user.fullname if request.user.fullname is not None else request.user.email,
    #                      # reason=request.json['change'].get('reason', None) if 'change' in request.json else None,
    #                      reason=None,
    #                      date=request.json['change'].get('date', None) if 'change' in request.json else None

    #                      )

    # request.session.add(change)

    # create a copy of the request data with only the mutable columns
    plant = Plant.query.get_or_404(plant_id)
    for key, value in args.items():
        setattr(plant, key, value)


    # if change.from_location_id != request.plant.location_id:
    #     # the change quantity represent the number of plants tranferred to a new location
    #     change.quantity = request.plant.quantity
    #     change.to_location_id = request.plant.location_id
    # elif request.plant.quantity < change.quantity:
    #     # the change quantity represents the number of plants removed from a location
    #     change.quantity = request.plant.quantity - change.quantity
    # else:
    #     # the change quantity represents the number of plants added to a location
    #     change.quantity = request.plant.quantity - change.quantity

    db.session.commit()
    return utils.json_response(plant.jsonify())


@api.route("/plant", methods=['POST'])
@login_required
@use_args({
    'location_id': fields.Int(required=True),
    'accession_id': fields.Int(required=True),
    'code': fields.String()
})
def post_plant(args):
    location = Location.query.filter_by(id=args['location_id']).first()
    if not location:
        abort(422, "Invalid location id")

    accession = db.Accession.query.filter_by(id=args['accession_id']).first()
    if not accession:
        abort(422, "Invalid session id")

    plant = Plant(**args)
    db.session.add(plant)

    # change = PlantChange(to_location_id=plant.location_id,
    #                      quantity=plant.quantity,  # store original quantity
    #                      person=request.user.fullname if request.user.fullname is not None else request.user.email,
    #                      #reason=request.json['change'].get('reason', None) if 'change' in request.json else None,
    #                      reason=None,
    #                      date=request.json['change'].get('date', None) if 'change' in request.json else None
    #                      )
    # change.plant = plant
    # request.session.add(change)

    db.session.commit()
    return utils.json_response(plant.jsonify(), 201)


@api.route("/plant/<int:plant_id>", methods=['DELETE'])
@login_required
def delete_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    db.session.delete(plant)
    db.session.commit()
    return '', 204


@api.route("/plant/<int:plant_id>/count")
@login_required
@use_args({
    'relation': fields.DelimitedList(fields.String(), required=True)
})
def plant_count(args, plant_id):
    data = {}
    plant = Plant.query.get_or_404(plant_id)
    for relation in args['relation']:
        _, base = relation.rsplit('/', 1)
        data[base] = utils.count_relation(plant, relation)
    return utils.json_response(data)
