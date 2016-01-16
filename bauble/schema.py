from functools import lru_cache

from marshmallow import fields
from marshmallow_sqlalchemy import (ModelSchema as _ModelSchema,
                                    ModelConverter as _ModelConverter)
from sqlalchemy import func, inspect, Column, DateTime, Integer, MetaData
from sqlalchemy.orm import ColumnProperty, Mapper, RelationshipProperty


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


@lru_cache()
def schema_class_factory(model_cls):
    import bauble.db as db

    mapper = inspect(model_cls)
    if not isinstance(mapper, Mapper):
        return schema_class_factory(type(model_cls))

    class ModelSchema(DefaultSchema):

        class Meta:
            model = model_cls
            dump_only = ['str']
            sqla_session = db.session
            strict = True
            model_converter = ModelConverter

    many_to_one_filter = lambda prop: prop.direction.name == "MANYTOONE"
    for prop in filter(many_to_one_filter, mapper.relationships):
        ModelSchema._declared_fields[prop.key] \
            = fields.Nested(schema_class_factory(prop.mapper.class_), dump_only=True)

    if hasattr(model_cls, '_additional_schema_fields'):
        ModelSchema._declared_fields.update(model_cls._additional_schema_fields)

    return ModelSchema

def schema_factory(cls, *args, **kwargs):
    return schema_class_factory(cls)(*args, **kwargs)
