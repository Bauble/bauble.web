from functools import lru_cache, partialmethod

from marshmallow import Schema
import marshmallow.fields as fields
from marshmallow.validate import OneOf
from wtforms import Form
import wtforms.fields as wtf_fields

import bauble.db as db
from bauble.schema import schema_class_factory


def string_converter(field):
    return wtf_fields.StringField()

def integer_converter(field):
    return wtf_fields.IntegerField()

def field_converter(field):
    for v in field.validators:
        if isinstance(v, OneOf):
            # TODO: need to be able to get the values and labels from the enum
            return wtf_fields.SelectField(choices=[(c, c) for c in v.choices])

    return wtf_fields.StringField()

def datetime_converter(field):
    # TODO: if has a OneOf validator then make it a SelectField
    return wtf_fields.DateTimeField()

def date_converter(field):
    # TODO: if has a OneOf validator then make it a SelectField
    return wtf_fields.DateField()

def boolean_converter(field):
    return wtf_fields.BooleanField()

def float_converter(field):
    return wtf_fields.FloatField()

def nested_converted(field):
    print('field: ', field)
    print('dir(field): ', dir(field))
    return wtf_fields.FormField()


CONVERTER_MAP = {
    fields.Integer: integer_converter,
    fields.Int: integer_converter,

    fields.String: string_converter,
    fields.Str: string_converter,

    fields.DateTime: datetime_converter,
    fields.Date: date_converter,

    fields.Boolean: boolean_converter,
    fields.Float: float_converter,

    fields.Field: field_converter,

    # TODO: function fields should only be dump only and can be skipped
    fields.Function: field_converter,

    fields.Raw: field_converter,

    # fields.Nested: nested_converted
    fields.Nested: field_converter

}

class MarshmallowForm(Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__schema__ = self.__schema_cls__()

    @property
    def errors(self):
        errors = super().errors()
        errors.update(self.__schema__)

    @classmethod
    def from_schema(cls, schema):
        # TODO: what about just creating a schema dynamically...this would allow
        # us to extend an existing form instead of creating a new one from scratch
        schema_cls = type(schema) if isinstance(schema, Schema) else schema
        form_cls = type(schema_cls.__name__ + 'Form', (MarshmallowForm, ), {
            '__schema_cls__': schema_cls
        })

        for name, field in schema_cls._declared_fields.items():
            converter = CONVERTER_MAP.get(type(field), None)
            if converter is None:
                raise ValueError("Could not convert field '{}.{}' of type {}."
                                 .format(schema_cls.Meta.model.__name__, name, type(field)))

            dest_field = converter(field)
            setattr(form_cls, name, dest_field)
            # print('{} validators: '.format(name), field.validators)
            validator_methods = {}
            for validator in field.validators:
                # print('validator: ', validator)

                def validator_wrapper(form):
                    validator
                validator_methods['validate_{}'.format(name)] = partialmethod(schema)
            #     setattr(form_cls, 'validate_{}'.format(name), partialmethod)

            # form_cls.__dict__.update(validator_methods)

        return form_cls


@lru_cache()
def form_class_factory(model):
    schema_cls = schema_class_factory(model)
    return MarshmallowForm.from_schema(schema_cls)


def form_factory(model, **form_kwargs):
    form_kwargs['obj'] = model
    return form_class_factory(model)(**form_kwargs)


# rails-like helper
form_for = form_factory
