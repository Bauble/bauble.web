from flask import redirect, request, url_for
from flask.ext.login import login_required
import sqlalchemy.orm as orm
from webargs import fields
from webargs.flaskparser import use_args

import bauble.db as db
from bauble.forms import form_factory
from bauble.models import Taxon
from bauble.middleware import use_model
from bauble.resource import Resource
from bauble.schema import schema_factory
import bauble.utils as utils

resource = Resource('taxon', __name__)

@resource.index
def index():
    taxa = Taxon.query.all()
    return resource.render_json(taxa)


@resource.show
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
@use_model(Taxon)
def new(taxon):
    return resource.render_html(taxon=taxon, form=form_factory(taxon))


@resource.create
@login_required
def create():
    taxon, errors = schema_factory(Taxon).load(request.params)
    if errors:
        if request.prefers_json:
            return resource.render_json(errors, status=422)
        return resource.render_html('new.html.jinja', form=form_factory(taxon))

    db.session.add(taxon)
    db.session.commit()
    if request.prefers_json:
        return resource.render_json(taxon, status=201)
    return resource.render_html('edit.html.jinja', taxon=taxon,
                                form=form_factory(taxon), status=201)


@resource.update
@login_required
@use_model(Taxon)
def update(taxon, id):
    db.session.commit()
    if request.prefers_json:
        return resource.render_json(taxon)
    # return resource.render_html(taxon=taxon, form=form_factory(taxon))
    return redirect(url_for('.edit', id=id))


@resource.edit
@login_required
def edit(id):
    taxon = Taxon.query.get_or_404(id)
    return resource.render_html(taxon=taxon, form=form_factory(taxon))


@resource.destroy
@login_required
@use_model(Taxon)
def destroy(taxon, id):
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
