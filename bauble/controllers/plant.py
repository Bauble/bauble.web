from flask import redirect, request, url_for
from flask.ext.login import login_required
import sqlalchemy.orm as orm
from webargs import fields
from webargs.flaskparser import use_args

import bauble.db as db
from bauble.forms import form_factory
from bauble.models import Plant
from bauble.middleware import use_model
from bauble.resource import Resource
from bauble.schema import schema_factory
import bauble.utils as utils

resource = Resource('plant', __name__)

@resource.index
@login_required
def index():
    taxa = Plant.query.all()
    return resource.render_json(taxa)

@resource.show
@login_required
@use_model(Plant)
def show(plant, id):
    if request.prefers_json:
        return resource.render_json(plant)

    # relations = ['/plants', '/plants/plants']
    # counts = {}
    # for relation in relations:
    #     _, base = relation.rsplit('/', 1)
    #     counts[base] = utils.count_relation(plant, relation)

    return resource.render_html(plant=plant, counts=counts)

@resource.new
@login_required
@use_model(Plant)
def new(plant):
    return resource.render_html(plant=plant, form=form_factory(plant))


@resource.create
@login_required
def create():
    plant, errors = schema_factory(Plant).load(request.params)
    if errors:
        if request.prefers_json:
            return resource.render_json(errors, status=422)
        return resource.render_html(template_name='new.html.jinja', plant=plant,
                                    form=form_factory(plant))

    db.session.add(plant)
    db.session.commit()
    if request.prefers_json:
        return resource.render_json(plant, status=201)
    return resource.render_html(template_name='edit.html.jinja', plant=plant,
                                form=form_factory(plant), status=201)


@resource.update
@login_required
@use_model(Plant)
def update(plant, id):
    db.session.commit()
    if request.prefers_json:
        return resource.render_json(plant)
    # return resource.render_html(plant=plant, form=form_factory(plant))
    return redirect(url_for('.edit', id=id))


@resource.edit
@login_required
def edit(id):
    plant = Plant.query.get_or_404(id)
    if request.prefers_json:
        return resource.render_json(plant)
    return resource.render_html(plant=plant, form=form_factory(plant))

@resource.destroy
@login_required
@use_model(Plant)
def destroy(plant, id):
    db.session.delete(plant)
    db.session.commit()
    return '', 204


@resource.route("/<int:id>/count")
@login_required
@use_args({
    'relation': fields.DelimitedList(fields.String(), required=True)
})
def plant_count(args, id):
    data = {}
    plant = Plant.query.get_or_404(id)
    for relation in args['relation']:
        _, base = relation.rsplit('/', 1)
        data[base] = utils.count_relation(plant, relation)
    return utils.json_response(data)
