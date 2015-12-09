import re
import sys

from attrdict import AttrDict
from flask.ext.sqlalchemy import (SQLAlchemy, Model as ExtModel, _BoundDeclarativeMeta,
                                  _QueryProperty)
from flask.ext.migrate import Migrate
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow_sqlalchemy import (ModelSchema as _ModelSchema,
                                    ModelConverter as _ModelConverter)
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

class ModelConverter(_ModelConverter):

    def fields_for_model(self, model, *args, **kwargs):
        kwargs['include_fk'] = True
        exclude = kwargs.pop('exclude', tuple())
        # exclude relation properties by default...the nested fields for
        # MANYTOONE relationships are added in DBPlugin._init_schema so we
        # can late bind the nested fields after all the schemas have been added
        exclude += tuple(p.key for p in inspect(model).relationships)
        return super().fields_for_model(model, *args, exclude=exclude, **kwargs)

    def _get_field_kwargs_for_property(self, prop):
        kwargs = super()._get_field_kwargs_for_property(prop)
        if isinstance(prop, RelationshipProperty):
            kwargs['dump_only'] = True
        kwargs.update(prop.class_attribute.info.get('field_kwargs', {}))
        return kwargs


class DefaultSchema(_ModelSchema):
    str = fields.String(dump_only=True)


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

        schema_cls = schema_cls if schema_cls is not None else cls.__schema__
        data, err = schema_cls().dump(instance, **kwargs)
        if len(err) > 0:
            raise SerializationError(err)
        return data


    @hybrid_property
    def str(self):
        return str(self)


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
        import bauble.models # import all models
        nested_fields = []

        for cls in plugin.Model._decl_class_registry.values():
            if not hasattr(cls, '__mapper__'):
                continue

            # nest many to one fields
            nested_fields.extend([cls, p] for p in inspect(cls).relationships
                                 if p.direction.name == 'MANYTOONE')

            class ModelSchema(DefaultSchema):
                class Meta:
                    model = cls
                    dump_only = ['str']
                    sqla_session = self.session
                    strict = True
                    model_converter = ModelConverter

            if hasattr(cls, '_additional_schema_fields'):
                ModelSchema._declared_fields.update(cls._additional_schema_fields)

            cls.__schema__ = ModelSchema

        # late bind the nested property after all the parent schema classes have
        # been created
        for cls, prop in nested_fields:
            cls.__schema__._declared_fields[prop.key] \
                = fields.Nested(prop.mapper.class_.__schema__, dump_only=True)


    def make_declarative_base(self, *args):
        """Creates the declarative base."""
        base = declarative_base(cls=_Model, name='Model', metadata=self.metadata,
                                metaclass=_BoundDeclarativeMeta)
        base.query = _QueryProperty(self)
        return base


plugin = DBPlugin()
plugin.ma = plugin.marshmallow = ma
sys.modules[__name__] = plugin
