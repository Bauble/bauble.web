from flask import redirect, request, url_for
from flask.ext.login import login_required
import sqlalchemy.orm as orm
from webargs import fields
from webargs.flaskparser import use_args

import bauble.db as db
from bauble.forms import form_factory
from bauble.models import Genus
from bauble.middleware import use_model
from bauble.resource import Resource
from bauble.schema import schema_factory
import bauble.utils as utils

resource = Resource('genus', __name__)

@resource.index
def index():
    genera = Genus.query.all()
    if request.prefers_json:
        return resource.render_json(genera)

    return resource.render_html(genera=genera)

@resource.show
def show(id):
    genus = Genus.query \
                 .options(orm.joinedload(*Genus.synonyms.attr)) \
                 .get_or_404(id)
    if request.prefers_json:
        return resource.render_json(genus)

    relations = ['/taxa', '/taxa/accessions', '/taxa/accessions/plants']
    counts = {}
    for relation in relations:
        _, base = relation.rsplit('/', 1)
        counts[base] = utils.count_relation(genus, relation)

    return resource.render_html(genus=genus, counts=counts)


@resource.new
@login_required
def new():
    genus = Genus()
    return resource.render_html(genus=genus, form=form_factory(genus))


@resource.create
@login_required
def create():
    genus = Genus()
    form = resource.save_request_params(genus)

    if request.prefers_json:
        return (resource.render_json(genus, status=201)
                if not form.errors
                else resource.render_json_errors(form.errors))

    return resource.render_html('new', status=201, genus=genus, form=form)


@resource.update
@login_required
def update(id):
    genus = Genus.query.get_or_404(id)
    form = resource.save_request_params(genus)
    if request.prefers_json:
        return (resource.render_json(genus)
                if not form.errors
                else resource.render_json_errors(form.errors))

    return resource.render_html('edit', genus=genus, form=form)


@resource.edit
@login_required
def edit(id):
    genus = Genus.query.get_or_404(id)
    return resource.render_html(genus=genus, form=form_factory(genus))


@resource.destroy
@login_required
def destroy(id):
    genus = Genus.query.get_or_404(id)
    db.session.delete(genus)
    db.session.commit()
    return '', 204


@resource.route("/<int:id>/count")
@login_required
@use_args({
    'relation': fields.DelimitedList(fields.String(), required=True)
})
def genus_count(args, id):
    data = {}
    genus = Genus.query.get_or_404(id)
    for relation in args['relation']:
        _, base = relation.rsplit('/', 1)
        data[base] = utils.count_relation(genus, relation)
    return utils.json_response(data)
