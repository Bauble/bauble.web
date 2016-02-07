import re
import sys

from flask.ext.sqlalchemy import (SQLAlchemy, Model as ExtModel, _BoundDeclarativeMeta,
                                  _QueryProperty)
from flask.ext.migrate import Migrate
from flask_marshmallow import Marshmallow
from sqlalchemy import func, Column, DateTime, Integer, MetaData
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from bauble.schema import schema_factory
from bauble.utils import combomethod

ma = Marshmallow()

class SerializationError(Exception):

    def __init__(self, errors):
        self.errors = errors
        super().__init__()


class _Model(ExtModel):
    """The default Model base class.
    """

    @declared_attr
    def __tablename__(cls):
        # return underscore cased class name
        return re.sub('(?!^)([A-Z]+)', r'_\1', cls.__name__).lower()

    id = Column(Integer, primary_key=True, autoincrement=True,
                info={'field_kwargs': {'dump_only': True}})
    created_at = Column(DateTime(True), server_default=func.now(),
                        nullable=False, info={'field_kwargs': {'dump_only': True}})
    updated_at = Column(DateTime(True), server_default=func.now(),
                        nullable=False, onupdate=func.now(),
                        info={'field_kwargs': {'dump_only': True}})

    @combomethod
    def jsonify(param, *args, schema_cls=None, **kwargs):
        cls = type(param) if isinstance(param, _Model) else param
        instance = param if isinstance(param, _Model) else args[0]

        schema = schema_factory(cls)
        data, err = schema.dump(instance, **kwargs)
        if len(err) > 0:
            raise SerializationError(err)
        return data


    def str(self):
        return str(self)

    @property
    def has_errors(self):
        return hasattr(self, '_errors') and len(self._errors) > 0


class DBPlugin(SQLAlchemy):

    metadata = MetaData()

    def init_app(self, app):
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get('DATABASE_URL')
        super().init_app(app)
        ma.init_app(app)
        Migrate(app, self)


    def make_declarative_base(self, *args):
        """Creates the declarative base."""
        base = declarative_base(cls=_Model, name='Model', metadata=self.metadata,
                                metaclass=_BoundDeclarativeMeta)
        base.query = _QueryProperty(self)
        return base


plugin = DBPlugin()
plugin.ma = plugin.marshmallow = ma
sys.modules[__name__] = plugin
