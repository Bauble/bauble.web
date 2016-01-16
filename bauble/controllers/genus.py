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
    return resource.render_json(genera)

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
    return resource.render_html(genus=genus, form=form_factory(genus))


@resource.create
@login_required
def create():
    genus, errors = schema_factory(Genus).load(request.params)
    if errors:
        if request.prefers_json:
            return resource.render_json(errors, status=422)
        return resource.render_html('new.html.jinja', form=form_factory(genus))

    db.session.add(genus)
    db.session.commit()
    if request.prefers_json:
        return resource.render_json(genus, status=201)
    return resource.render_html('edit.html.jinja', genus=genus, form=form_factory(genus),
                                status=201)


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
    return resource.render_html(genus=genus, form=form_factory(genus))


@resource.destroy
@login_required
@use_model(Genus)
def destroy(genus, id):
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
