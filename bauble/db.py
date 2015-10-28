import re
import sys

from attrdict import AttrDict
from flask.ext.sqlalchemy import (SQLAlchemy, Model as ExtModel, _BoundDeclarativeMeta,
                                  _QueryProperty)
from flask.ext.migrate import Migrate
from flask_marshmallow import Marshmallow
from marshmallow import fields
from sqlalchemy import func, inspect, Column, DateTime, Integer, MetaData
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from bauble.utils import combomethod

ma = Marshmallow()


class SerializationError(Exception):

    def __init__(self, errors):
        self.errors = errors
        super().__init__()


class _BaseSchema(ma.Schema):

    def dump(self, *args, **kwargs):
        """Wrap marshmallow.Schema to raise a SerializationError on error.
        """
        data, err = super().dump(*args, **kwargs)
        if len(err) > 0:
            raise SerializationError(err)
        return data


class _JSONSchema(_BaseSchema, ma.ModelSchema):
    str = fields.String(dump_only=True)



class _Model(ExtModel):
    """The default Model base class.
    """

    @declared_attr
    def __tablename__(cls):
        # return underscore cased class name
        return re.sub('(?!^)([A-Z]+)', r'_\1', cls.__name__).lower()

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(True), server_default=func.now())
    updated_at = Column(DateTime(True), server_default=func.now(),
                        onupdate=func.now())

    json_default = None

    @classmethod
    def _create_default_schema(cls):
        if cls.json_default is None:
            cls.json_default = tuple(c for c in inspect(cls).mapper.columns.keys()
                                     if not c.startswith('_')) + ('str',)

        class JSONSchema(_JSONSchema):
            class Meta:
                model = cls
                fields = cls.json_default

        return JSONSchema
    _default_schema_cls = None


    @combomethod
    def jsonify(param, *args, schema_cls=None, **kwargs):
        cls = type(param) if isinstance(param, _Model) else param
        instance = param if isinstance(param, _Model) else args[0]

        # use the default schema if no schema_cls was passed
        if schema_cls is None:
            if cls._default_schema_cls is None:
                # create the default schema cls if it hasn't been created yet
                cls._default_schema_cls = param._create_default_schema()
            schema_cls = cls._default_schema_cls

        return schema_cls().dump(instance, **kwargs)


    # @declared_attr
    @hybrid_property
    def str(self):
        str(self)


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
# plugin.Schema = Schema
sys.modules[__name__] = plugin
