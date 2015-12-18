from flask import request
from flask.ext.login import login_required
import sqlalchemy.orm as orm

import bauble.db as db
from bauble.forms import form_factory
from bauble.models import Family
from bauble.resource import Resource
import bauble.utils as utils


resource = Resource('family', __name__)

@resource.index
def index(families):
    families = Family.query.all()
    if request.accept_mimetypes.best == 'application/json':
        return resource.render_json(families)
    return resource.render_html(families=families)

@resource.show
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
def new():
    family = Family()
    return resource.render_html(family=family, form=form_factory(family))

@resource.create
def create(self):
    family = Family()
    if request.prefers_json:
        return resource.rendor_json(family)
    return self.render_html(family=family, form=form_factory(family))

@resource.edit
def edit(id):
    family = Family.query.get_or_404(id)
    if request.prefers_json:
        return resource.rendor_json(family)
    return resource.render_html(family=family, form=form_factory(family))

# @resource.destroy
def destroy(self, id):
    family = Family.query.get_or_404(id)
    db.session.delete(family)
    db.session.commit()
    return '', 204

# @route()
def count(self, id):
    pass


class FamilyResource(Resource):
    pass


    # def index(self):
    #     families = Family.query.all()
    #     if request.accept_mimetypes.best == 'application/json':
    #         return self.render_json(families)
    #     return self.render_html(families=families)

    # def show(self, id):
    #     family = Family.query.get_or_404(id)
    #     if request.accept_mimetypes.best == 'application/json':
    #         return self.render_json(family)
    #     return self.render_html(family=family)

    # def new(self):
    #     family = Family()
    #     return self.render_html(family=family, form=form_factory(family))

    # def destroy(self, id):
    #     family = Family.query.get_or_404(id)
    #     db.session.delete(family)
    #     db.session.commit()
    #     return '', 204

    # @route()
    # def count(self, id):
    #     pass
