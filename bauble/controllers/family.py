from flask import current_app, redirect, request, url_for
from flask.ext.login import login_required
import sqlalchemy.orm as orm
from webargs import fields
from webargs.flaskparser import use_args

import bauble.db as db
from bauble.forms import form_factory
from bauble.models import Family
from bauble.middleware import use_model
from bauble.resource import Resource
import bauble.utils as utils

resource = Resource('family', __name__)

@resource.index
@login_required
def index():
    families = Family.query.all()
    if request.prefers_json:
        return resource.render_json(families)

    return resource.render_html(families=families)


@resource.show
@login_required
def show(id):
    family = Family.query \
                   .options(orm.joinedload(*Family.synonyms.attr)) \
                   .get_or_404(id)
    if request.prefers_json:
        return resource.render_json(family)

    relations = ['/genera', '/genera/taxa', '/genera/taxa/accessions',
                 '/genera/taxa/accessions/plants']
    counts = {}
    for relation in relations:
        _, base = relation.rsplit('/', 1)
        counts[base] = utils.count_relation(family, relation)

    return resource.render_html(family=family, counts=counts)


@resource.new
@login_required
def new():
    family = Family()
    return resource.render_html(family=family, form=form_factory(family))


@resource.create
@login_required
def create():
    family = Family()
    form = resource.save_request_params(family)

    if request.prefers_json:
        return (resource.render_json(family, status=201)
                if not form.errors
                else resource.render_json_errors(form.errors))

    return resource.render_html('new', status=201, family=family, form=form)


@resource.update
@login_required
def update(id):
    family = Family.query.get_or_404(id)
    form = resource.save_request_params(family)
    if request.prefers_json:
        return (resource.render_json(family)
                if not form.errors
                else resource.render_json_errors(form.errors))

    return resource.render_html('edit', family=family, form=form)


@resource.edit
@login_required
def edit(id):
    family = Family.query.get_or_404(id)
    return resource.render_html(family=family, form=form_factory(family))


@resource.destroy
@login_required
def destroy(id):
    family = Family.query.get_or_404(id)
    db.session.delete(family)
    db.session.commit()
    return '', 204


@resource.route("/<int:family_id>/count")
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
