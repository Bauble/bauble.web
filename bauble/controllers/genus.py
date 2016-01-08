from flask import redirect, request, url_for
from flask.ext.login import login_required
import sqlalchemy.orm as orm

import bauble.db as db
from bauble.forms import form_factory
from bauble.models import Genus
from bauble.middleware import use_model
from bauble.resource import Resource
from bauble.schema import schema_factory
import bauble.utils as utils

resource = Resource('genus', __name__)

@resource.index
def index(genera):
    genera = Genus.query.all()
    if request.accept_mimetypes.best == 'application/json':
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
@use_model(Genus)
def new(genus):
    # genus = Genus()
    return resource.render_html(genus=genus, form=form_factory(genus))


@resource.create
@login_required
def create():
    genus, errors = schema_factory(Genus).load(request.get_json())
    if errors:
        if request.prefers_json:
            return resource.render_json(errors)
        return resource.render_html('new.html.jinja', form=form_factory(genus))

    db.session.add(genus)
    db.session.commit()
    if request.prefers_json:
        return resource.render_json(genus)
    return resource.render_html('edit.html.jinja', form=form_factory(genus))


@resource.update
@login_required
@use_model(Genus)
def update(genus, id):
    db.session.commit()
    if request.prefers_json:
        return resource.render_json(genus)
    # return resource.render_html(genus=genus, form=form_factory(genus))
    return redirect(url_for('.edit', id=id))

@resource.edit
@login_required
def edit(id):
    genus = Genus.query.get_or_404(id)
    if request.prefers_json:
        return resource.render_json(genus)
    return resource.render_html(genus=genus, form=form_factory(genus))

@resource.destroy
@login_required
@use_model(Genus)
def destroy(genus, id):
    db.session.delete(genus)
    db.session.commit()
    return '', 204

# @route()
def count(id):
    pass
