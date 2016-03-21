from flask import redirect, request, url_for
from flask.ext.login import login_required
import sqlalchemy.orm as orm
from webargs import fields
from webargs.flaskparser import use_args

import bauble.db as db
from bauble.forms import form_factory
from bauble.models import Location
from bauble.middleware import use_model
from bauble.resource import Resource
from bauble.schema import schema_factory
import bauble.utils as utils

resource = Resource('location', __name__)

@resource.index
@login_required
def index():
    taxa = Location.query.all()
    return resource.render_json(taxa)

@resource.show
@login_required
@use_model(Location)
def show(location, id):
    if request.prefers_json:
        return resource.render_json(location)

    # relations = ['/locations', '/locations/locations']
    # counts = {}
    # for relation in relations:
    #     _, base = relation.rsplit('/', 1)
    #     counts[base] = utils.count_relation(location, relation)

    return resource.render_html(location=location, counts=counts)

@resource.new
@login_required
@use_model(Location)
def new(location):
    return resource.render_html(location=location, form=form_factory(location))


@resource.create
@login_required
@login_required
def create():
    location, errors = schema_factory(Location).load(request.params)
    if errors:
        if request.prefers_json:
            return resource.render_json(errors, status=422)
        return resource.render_html(template_name='new.html.jinja', location=location,
                                    form=form_factory(location))

    db.session.add(location)
    db.session.commit()
    if request.prefers_json:
        return resource.render_json(location, status=201)
    return resource.render_html(template_name='edit.html.jinja', location=location,
                                form=form_factory(location), status=201)


@resource.update
@login_required
@use_model(Location)
def update(location, id):
    db.session.commit()
    if request.prefers_json:
        return resource.render_json(location)
    # return resource.render_html(location=location, form=form_factory(location))
    return redirect(url_for('.edit', id=id))


@resource.edit
@login_required
def edit(id):
    location = Location.query.get_or_404(id)
    if request.prefers_json:
        return resource.render_json(location)
    return resource.render_html(location=location, form=form_factory(location))

@resource.destroy
@login_required
@use_model(Location)
def destroy(location, id):
    db.session.delete(location)
    db.session.commit()
    return '', 204


@resource.route("/<int:id>/count")
@login_required
@use_args({
    'relation': fields.DelimitedList(fields.String(), required=True)
})
def location_count(args, id):
    data = {}
    location = Location.query.get_or_404(id)
    for relation in args['relation']:
        _, base = relation.rsplit('/', 1)
        data[base] = utils.count_relation(location, relation)
    return utils.json_response(data)
