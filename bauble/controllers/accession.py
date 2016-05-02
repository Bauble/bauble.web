from flask import abort, redirect, request, url_for
from flask.ext.login import login_required
import sqlalchemy.orm as orm
from webargs import fields
from webargs.flaskparser import use_args

import bauble.db as db
from bauble.forms import form_factory
from bauble.models import Accession
from bauble.middleware import use_model
from bauble.resource import Resource
from bauble.schema import schema_factory
import bauble.utils as utils

resource = Resource('accession', __name__)

@resource.index
@login_required
def index():
    accessions = Accession.query.all()
    if not request.accept_json:
        abort(406)

    return resource.render_json(accessions)


@resource.show
@login_required
def show(id):
    accession = Accession.query \
                 .options(orm.joinedload(*Accession.synonyms.attr)) \
                 .get_or_404(id)
    if request.prefers_json:
        return resource.render_json(accession)

    relations = ['/accessions', '/accessions/plants']
    counts = {}
    for relation in relations:
        _, base = relation.rsplit('/', 1)
        counts[base] = utils.count_relation(accession, relation)

    return resource.render_html(accession=accession, counts=counts)

@resource.new
@login_required
def new():
    accession = Accession()
    return resource.render_html(accession=accession, form=form_factory(accession))


@resource.create
@login_required
def create():
    accession, errors = schema_factory(Accession).load(request.params)
    if errors:
        if request.prefers_json:
            return resource.render_json(errors, status=422)
        return resource.render_html(template_name='new.html.jinja', accession=accession,
                                    form=form_factory(accession))

    db.session.add(accession)
    db.session.commit()
    if request.prefers_json:
        return resource.render_json(accession, status=201)
    return resource.render_html(template_name='edit.html.jinja', accession=accession,
                                form=form_factory(accession), status=201)


@resource.update
@login_required
@use_model(Accession)
def update(accession, id):
    db.session.commit()
    if request.prefers_json:
        return resource.render_json(accession)
    # return resource.render_html(accession=accession, form=form_factory(accession))
    return redirect(url_for('.edit', id=id))


@resource.edit
@login_required
def edit(id):
    accession = Accession.query.get_or_404(id)
    if request.prefers_json:
        return resource.render_json(accession)
    return resource.render_html(accession=accession, form=form_factory(accession))

@resource.destroy
@login_required
@use_model(Accession)
def destroy(accession, id):
    db.session.delete(accession)
    db.session.commit()
    return '', 204


@resource.route("/<int:id>/count")
@login_required
@use_args({
    'relation': fields.DelimitedList(fields.String(), required=True)
})
def accession_count(args, id):
    data = {}
    accession = Accession.query.get_or_404(id)
    for relation in args['relation']:
        _, base = relation.rsplit('/', 1)
        data[base] = utils.count_relation(accession, relation)
    return utils.json_response(data)
