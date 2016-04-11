from flask.ext.login import login_required
from flask import abort, request
import sqlalchemy.orm as orm

import bauble.db as db
from bauble.models import Taxon, VernacularName
from bauble.resource import Resource

resource = Resource('vernacular_name', __name__,
                    url_prefix='/taxon/<int:taxon_id>/vernacular_name')

@resource.index
@login_required
def index(taxon_id):
    taxon = Taxon.query.options(orm.joinedload('vernacular_names')).get_or_404(taxon_id)

    if not request.accept_json:
        # TODO: send paginated response of all vernacular_name and potentially
        # apply filters using the search module
        abort(406)

    return resource.render_json(taxon.vernacular_names)


@resource.show
@login_required
def show(taxon_id, id):
    vernacular_name = VernacularName.query.get_or_404(id)
    if vernacular_name.taxon_id != taxon_id:
        abort(404)

    if not request.accept_json:
        # TODO: send paginated response of all vernacular_name and potentially
        # apply filters using the search module
        abort(406)

    return resource.render_json(vernacular_name)


@resource.create
@login_required
def create(taxon_id):
    taxon = Taxon.query.get_or_404(taxon_id)
    vernacular_name = VernacularName()
    taxon.vernacular_names.append(vernacular_name)
    form = resource.save_request_params(vernacular_name)

    if request.prefers_json:
        return (resource.render_json(vernacular_name, status=201)
                if not form.errors
                else resource.render_json_errors(form.errors))

    return '', 201


@resource.update
@login_required
def update(taxon_id, id):
    vernacular_name = VernacularName.query.get_or_404(id)
    if vernacular_name.taxon_id != taxon_id:
        abort(404)

    form = resource.save_request_params(vernacular_name)
    if request.prefers_json:
        return (resource.render_json(vernacular_name)
                if not form.errors
                else resource.render_json_errors(form.errors))

    return '', 204


@resource.destroy
@login_required
def destroy(taxon_id, id):
    vernacular_name = VernacularName.query.get_or_404(id)
    if vernacular_name.taxon_id != taxon_id:
        abort(404)

    db.session.delete(vernacular_name)
    db.session.commit()
    return '', 204
