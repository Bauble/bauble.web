from flask import abort, request
from flask.ext.login import login_required
import sqlalchemy.orm as orm
from webargs import fields
from webargs.flaskparser import use_args

import bauble.db as db
from bauble.forms import form_factory
from bauble.models import Geography, Taxon
from bauble.resource import Resource
import bauble.utils as utils

resource = Resource('taxon', __name__)

@resource.index
@login_required
def index():
    taxa = Taxon.query.all()
    if not request.accept_json:
        abort(406)

    return resource.render_json(taxa)


@resource.show
@login_required
def show(id):
    taxon = Taxon.query \
                 .options(orm.joinedload(*Taxon.synonyms.attr)) \
                 .get_or_404(id)
    if request.prefers_json:
        return resource.render_json(taxon)

    relations = ['/accessions', '/accessions/plants']
    counts = {}
    for relation in relations:
        _, base = relation.rsplit('/', 1)
        counts[base] = utils.count_relation(taxon, relation)

    return resource.render_html(taxon=taxon, counts=counts)


@resource.new
@login_required
def new():
    taxon = Taxon()
    geographies = Geography.query.all()
    return resource.render_html(taxon=taxon, geographies=geographies,
                                form=form_factory(taxon))


@resource.create
@login_required
def create():
    taxon = Taxon()
    form = resource.save_request_params(taxon)

    # TODO: accept vernacular names for create only

    if request.prefers_json:
        return (resource.render_json(taxon, status=201)
                if not form.errors
                else resource.render_json_errors(form.errors))

    return resource.render_html('new', status=201, taxon=taxon, form=form)


@resource.update
@login_required
def update(id):
    taxon = Taxon.query.get_or_404(id)
    form = resource.save_request_params(taxon)
    if request.prefers_json:
        return (resource.render_json(taxon)
                if not form.errors
                else resource.render_json_errors(form.errors))

    return resource.render_html('edit', taxon=taxon, form=form)


@resource.edit
@login_required
def edit(id):
    taxon = Taxon.query.get_or_404(id)
    geographies = Geography.query.all()
    return resource.render_html(taxon=taxon, geographies=geographies,
                                form=form_factory(taxon))


@resource.destroy
@login_required
def destroy(id):
    taxon = Taxon.query.get_or_404(id)
    db.session.delete(taxon)
    db.session.commit()
    return '', 204


@resource.route("/<int:id>/count")
@login_required
@use_args({
    'relation': fields.DelimitedList(fields.String(), required=True)
})
def taxon_count(args, id):
    data = {}
    taxon = Taxon.query.get_or_404(id)
    for relation in args['relation']:
        _, base = relation.rsplit('/', 1)
        data[base] = utils.count_relation(taxon, relation)
    return utils.json_response(data)
