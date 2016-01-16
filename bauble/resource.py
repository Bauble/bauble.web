from functools import partial, wraps
import inspect

from flask import abort, render_template, Blueprint

import bauble.utils as utils


class Resource(Blueprint):

    def __init__(self, name, import_name, **kwargs):
        # name = kwargs.pop('name', model_cls.__name__.lower())
        kwargs.setdefault('url_prefix', '/{}'.format(name))
        super().__init__(name, import_name, **kwargs)

    def render_html(self, template_name=None, status=200, **context):
        if template_name is None:
            template_name = '{}.html.jinja'.format(self.current_action)
        return render_template('{}/{}'.format(self.name, template_name), **context), status

    def render_json(self, model, status=200):
        if hasattr(model, '__iter__'):
            data = type(model[0]).jsonify(model, many=True)
        else:
            data = model.jsonify()

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


    # def action(self, rule, **kwargs):
    #     def decorator(f):
    #         @wraps(f)
    #         def view_func(*args, **kwargs):
    #             print('__name__: ', __name__)
    #             self.current_action = __name__
    #             return f(*args, **kwargs)
    #         self.add_url_rule(rule, view_func=view_func)
    #     return decorator
