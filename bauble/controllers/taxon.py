from flask import abort, request
from flask.ext.login import login_required
from wtforms_alchemy import ModelFieldList, ModelForm, ModelFormField, model_form_factory
from wtforms.fields import FormField, BooleanField, StringField
import wtforms.widgets as widgets
import sqlalchemy.orm as orm
from webargs import fields
from webargs.flaskparser import use_args

import bauble.db as db
# from bauble.controllers.vernacular_name import Resource as VernacularNameResource
from bauble.forms import form_factory, form_class_factory, BaseModelForm
from bauble.models import Geography, Taxon, VernacularName, DefaultVernacularName
from bauble.resource import Resource
import bauble.utils as utils

resource = Resource('taxon', __name__)

class HiddenBooleanField(BooleanField):
    widget = widgets.HiddenInput()

class RelationshipFormMixin(BaseModelForm):
    destroy_ = HiddenBooleanField()

class OneToManyField(ModelFieldList):
    def __init__(self, model, *args, **kwargs):
        model_form = model_form_factory(RelationshipFormMixin)
        form_cls = form_class_factory(model, model_form, include_primary_keys=True)
        super().__init__(ModelFormField(form_cls), *args, **kwargs)


class OneToOneField(ModelFormField):
    def __init__(self, model, *args, **kwargs):
        model_form = model_form_factory(RelationshipFormMixin)
        form_cls = form_class_factory(model, model_form, include_primary_keys=True)
        super().__init__(form_cls, *args, **kwargs)


class TaxonForm(form_class_factory(Taxon)):
    vernacular_names = OneToManyField(VernacularName)

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
                                form=TaxonForm)
                                # form=form_factory(taxon))

def accept_nested(attribute, model):
    # TODO: maybe instead of having a accept nested we can just subclass
    # the form and use a wtfoms field enclosure: http://wtforms.readthedocs.io/en/latest/fields.html#field-enclosures
    def decorator(f):
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper
    return decorator

# def accept_nested_resources(model_or_form_cls, *kwargs):
#     form_cls = forms.form_class_factory(model_or_form_cls) \
#         if isinstance(db.Model) else model_or_form_Cls

#     class ExtendedForm(form_cls):

def process_nested_resource(param_name, resource_name):
    values = request.params.get(param_name, None)
    if values is None:
        return

    def forward_request(data):
        print('data: ', data)
        # TODO:

    if not isinstance(values, (list, tuple)):
        forward_request(values)
        return

    for val in values:
        forward_request(val)


@resource.create
@login_required
@accept_nested('vernacular_names', model=VernacularName)
def create():
    taxon = Taxon()
    form = resource.save_request_params(taxon, form=TaxonForm())

    process_nested_resource('vernacular_names',  'vernacular_name')

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
    taxon = Taxon.query \
                 .options(orm.joinedload('vernacular_names')) \
                 .get_or_404(id)
    geographies = Geography.query.all()
    return resource.render_html(taxon=taxon, geographies=geographies,
                                form=TaxonForm(obj=taxon))


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
