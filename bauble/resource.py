from functools import partial, wraps
import inspect

from flask import abort, current_app, render_template, Blueprint

import bauble.utils as utils
import bauble.db as db
from bauble.forms import form_factory

class Resource(Blueprint):

    def __init__(self, name, import_name, **kwargs):
        # name = kwargs.pop('name', model_cls.__name__.lower())
        kwargs.setdefault('url_prefix', '/{}'.format(name))
        super().__init__(name, import_name, **kwargs)

    def render_html(self, template_name=None, status=200, **context):
        if template_name is None:
            template_name = '{}.html.jinja'.format(self.current_action)
        elif '.' not in template_name:
            # template name can be just the base string
            template_name = '{}.html.jinja'.format(template_name)
        return render_template('{}/{}'.format(self.name, template_name), **context), status

    def render_json(self, model, status=200):
        if isinstance(model, (list, tuple))and len(model) > 0:
            data = type(model[0]).jsonify(model, many=True)
        elif isinstance(model, db.Model):
            data = model.jsonify()
        else:
            data = model

        return utils.json_response(data, status=status)

    def index(self, f):
        @wraps(f)
        def view_func(*args, **kwargs):
            # TODO: this state probably needs to be put in a thread local variable
            # to avoid race conditions, flaks.g or something else
            self.current_action = 'index'
            return f(*args, **kwargs)
        self.add_url_rule('', view_func=view_func, methods=['GET'])
        self.add_url_rule('.json', view_func=view_func, methods=['GET'])

    def new(self, f):
        @wraps(f)
        def view_func(*args, **kwargs):
            self.current_action = 'new'
            return f(*args, **kwargs)
        self.add_url_rule('/new', view_func=view_func, methods=['GET'])

    def edit(self, f):
        @wraps(f)
        def view_func(*args, **kwargs):
            self.current_action = 'edit'
            return f(*args, **kwargs)
        self.add_url_rule('/<int:id>/edit', view_func=view_func, methods=['GET'])

    def create(self, f):
        @wraps(f)
        def view_func(*args, **kwargs):
            self.current_action = 'create'
            return f(*args, **kwargs)
        self.add_url_rule('', view_func=view_func, methods=['POST'])
        self.add_url_rule('.json', view_func=view_func, methods=['POST'])
        # self.add_url_rule('/<int:id>', view_func=view_func, methods=['POST'])

    def update(self, f):
        @wraps(f)
        def view_func(*args, **kwargs):
            self.current_action = 'update'
            # TODO: verify CSRF
            return f(*args, **kwargs)
        self.add_url_rule('/<int:id>', view_func=view_func, methods=['PATCH', 'POST'])
        self.add_url_rule('/<int:id>.json', view_func=view_func, methods=['PATCH', 'POST'])

    def show(self, f):
        @wraps(f)
        def view_func(*args, **kwargs):
            self.current_action = 'show'
            return f(*args, **kwargs)
        self.add_url_rule('/<int:id>', view_func=view_func, methods=['GET'])
        self.add_url_rule('/<int:id>.json', view_func=view_func, methods=['GET'])

    def destroy(self, f):
        @wraps(f)
        def view_func(*args, **kwargs):
            self.current_action = 'destroy'
            return f(*args, **kwargs)
        self.add_url_rule('/<int:id>', view_func=view_func, methods=['DELETE'])
        self.add_url_rule('/<int:id>.json', view_func=view_func, methods=['DELETE'])


    def render_json_errors(self, errors):
        return utils.json_response(errors)

    def save_request_params(self, model, form=None):
        if form is None:
            form = form_factory(model)

        if form.validate_on_submit():
            form.populate_obj(model)
            # TODO: what happens if an exception is raised...could we have a
            # resource error handler....or a save_resource() that handles the commit
            # and transaction...we could probably go one step further and do the
            # validate on submit, populate and commit and handle error in one
            # function

            try:
                db.session.add(model)
                db.session.commit()
            except Exception as exc:
                form.errors['default'] = 'Could not save {}'.format(model.__class__.__name__.lower)
                current_app.logger.error(exc)

        return form

    # def action(self, rule, **kwargs):
    #     def decorator(f):
    #         @wraps(f)
    #         def view_func(*args, **kwargs):
    #             print('__name__: ', __name__)
    #             self.current_action = __name__
    #             return f(*args, **kwargs)
    #         self.add_url_rule(rule, view_func=view_func)
    #     return decorator
