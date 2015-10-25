
import bottle
from bottle import request
import sqlalchemy as sa
import sqlalchemy.orm as orm

from bauble import app, API_ROOT
from bauble.middleware import basic_auth
import bauble.model as model
import bauble.types as types

# these are the resources we can get the schema of
resource_map = {
    'family': model.Family,
    'genus': model.Genus,
    'taxon': model.Taxon,
    'accession': model.Accession,
    'plant': model.Plant,
    'location': model.Location,
    'geography': model.Geography,
}

@app.get(API_ROOT + "/<path:path>/schema")
@basic_auth
def get_schema(path):
    split_path = path.split('/')
    resource = split_path[0]
    relation = split_path[1:]

    try:
        model_class = resource_map[resource]
    except KeyError:
        bottle.abort(404)

    flags = request.query.flags
    if(flags):
        flags = flags.split(',')

    mapper = orm.class_mapper(model_class)

    # walk down the chain and get the relationships defined by the route
    for name in relation:
        # TODO: if we can't find a mapper what should we return...404 or just 400
        mapper = getattr(mapper.relationships, name).mapper
    schema = dict(columns={}, relations={})

    for name, column in mapper.columns.items():
        if name.startswith('_'):
            continue
        column_dict = dict(required=column.nullable)
        schema['columns'][name] = column_dict
        if isinstance(column.type, sa.String):
            column_dict['type'] = 'string'
            column_dict['length'] = column.type.length
        elif isinstance(column.type, sa.Integer):
            column_dict['type'] = 'int'
        elif isinstance(column.type, types.Enum):
            column_dict['type'] = 'list'
            column_dict['values'] = column.type.values
        elif isinstance(column.type, types.DateTime):
            column_dict['type'] = 'datetime'
        elif isinstance(column.type, types.Date):
            column_dict['type'] = 'date'
        elif isinstance(column.type, sa.Boolean):
            column_dict['type'] = 'boolean'
        else:
            raise Exception("Unknown type %s for column %s: " % (str(column.type), column.name))

    if 'scalars_only' in flags:
        schema['relations'] = [key for key, rel in mapper.relationships.items() if not key.startswith('_') and not rel.uselist]
    else:
        schema['relations'] = [key for key in mapper.relationships.keys() if not key.startswith('_')]

    return schema
