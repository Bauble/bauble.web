import re
import sys

from attrdict import AttrDict
from flask.ext.sqlalchemy import (SQLAlchemy, Model as ExtModel, _BoundDeclarativeMeta,
                                  _QueryProperty)
from flask.ext.migrate import Migrate
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema
from sqlalchemy import func, inspect, Column, DateTime, Integer, MetaData
from sqlalchemy.orm import ColumnProperty, RelationshipProperty
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from bauble.utils import combomethod

ma = Marshmallow()

class SerializationError(Exception):

    def __init__(self, errors):
        self.errors = errors
        super().__init__()


class _JSONSchema(ModelSchema):
    str = fields.String(dump_only=True)


class _MutableSchema(ModelSchema):
    pass


class _Model(ExtModel):
    """The default Model base class.
    """

    @declared_attr
    def __tablename__(cls):
        # return underscore cased class name
        return re.sub('(?!^)([A-Z]+)', r'_\1', cls.__name__).lower()

    id = Column(Integer, primary_key=True, autoincrement=True,
                info={'mutable': False})
    created_at = Column(DateTime(True), server_default=func.now(),
                        info={'mutable': False, 'jsonify': False})
    updated_at = Column(DateTime(True), server_default=func.now(),
                        onupdate=func.now(),
                        info={'mutable': False, 'jsonify': False})

    @combomethod
    def jsonify(param, *args, schema_cls=None, **kwargs):
        cls = type(param) if isinstance(param, _Model) else param
        instance = param if isinstance(param, _Model) else args[0]

        data, err = cls.JSONSchema().dump(instance, **kwargs)
        if len(err) > 0:
            raise SerializationError(err)
        return data


    # @hybrid_property
    @declared_attr
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
        self._init_schemas()

    def _init_schemas(self):
        import bauble.models
        json_nested_fields = []

        for cls in plugin.Model._decl_class_registry.values():
            if not hasattr(cls, '__mapper__'):
                continue
            mapper_cls = inspect(cls)
            json_fields = ['str']
            mutable_fields = []
            for attr_property in mapper_cls.attrs:
                attr_name = attr_property.key
                is_column = isinstance(attr_property, ColumnProperty)
                attr = getattr(cls, attr_name)
                if attr.info.get('jsonify', is_column):
                    if isinstance(attr_property, RelationshipProperty):
                        json_nested_fields.append((cls, attr_property))

                    json_fields.append(attr_name)

                # only columns can be mutable
                if is_column and attr.info.get('mutable', True):
                    mutable_fields.append(attr_name)

            class JSONSchema(_JSONSchema):
                class Meta:
                    model = cls
                    fields = json_fields
                    sqla_session = self.session
            cls.JSONSchema = JSONSchema

            class MutableSchema(_MutableSchema):
                class Meta:
                    model = cls
                    fields = mutable_fields
                    sqla_session = self.session
            cls.MutableSchema = MutableSchema

        # late bind the nested property after all the parent JSONSchema
        # classes have been created
        for cls, attr_property in json_nested_fields:
            cls.JSONSchema._declared_fields[attr_property.key] \
                = fields.Nested(attr_property.mapper.class_.JSONSchema)


    def make_declarative_base(self, *args):
        """Creates the declarative base."""
        base = declarative_base(cls=_Model, name='Model', metadata=self.metadata,
                                metaclass=_BoundDeclarativeMeta)
        base.query = _QueryProperty(self)
        return base


plugin = DBPlugin()
plugin.ma = plugin.marshmallow = ma
sys.modules[__name__] = plugin
