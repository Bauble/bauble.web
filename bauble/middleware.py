from flask import request

import bauble.db as db
import sqlalchemy as sa
import functools
# from webargs.core import Parser
from webargs.flaskparser import FlaskParser as Parser

parser = Parser()

def use_model(model_cls):
    """
    Load a model from the request args.

    This decorator will load an instance from primary keys defined in the
    request.view_args.  If a

    @use_model(Family)
    """
    def decorator(next):
        @functools.wraps(next)
        def wrapper(*args, **kwargs):
            # TODO: use a wrapper so we can namespace the instance property
            # values away from anything else that is passed to the route

            # if all the primary keys are available then load the request.view_args
            # then load the instance or 404 if its not found
            pk = [pk.key for pk in sa.inspect(model_cls).primary_key]
            instance = None

            # TODO: eager load any schema fields that are relationships
            if set(request.view_args.keys()) >= set(pk):
                ident = tuple(request.view_args[pk] for pk in pk)
                instance = model_cls.query.get_or_404(ident)

            # parse() uses ModelSchema.load will populate an instance from the request
            # when an instance is provided
            if instance is None:
                instance = model_cls()
            schema = model_cls.__schema_cls__(instance=instance)
            parser.parse(schema, request)
            return next(instance, *args, **kwargs)
        return wrapper
    return decorator
