import functools
from collections import UserDict
import re

from flask import json, current_app


def json_response(data, status=200, **kwargs):
    """Shortcut for building a flask JSON response."""
    if not isinstance(data, str):
        data = json.dumps(data)
    return current_app.response_class(data, status=status, mimetype='application/json',
                                      **kwargs)

class LinkHeader(UserDict):

    @staticmethod
    def from_str(str):
        link_header = LinkHeader()
        matches = re.findall('<(?P<url>.+?)>;\s+rel="(?P<rel>.+?)"+', str)
        for match in matches:
            url, rel = match
            link_header[rel] = url
        return link_header

    def __str__(self):
        return ', '.join(['<{}>; rel="{}"'.format(url, name)
                          for name, url in self.items()])


class combomethod(object):
    """All a method to be both a classmethod and an instance method

    http://stackoverflow.com/questions/2589690/creating-a-method-that-is-simultaneously-an-instance-and-class-method
    """
    def __init__(self, method):
        self.method = method

    def __get__(self, obj=None, objtype=None):
        @functools.wraps(self.method)
        def _wrapper(*args, **kwargs):
            if obj is not None:
                return self.method(obj, *args, **kwargs)
            else:
                return self.method(objtype, *args, **kwargs)
        return _wrapper


def count_relation(mapped_instance, relation):
    import bauble.db as db
    import sqlalchemy.orm as orm
    mapped_class = type(mapped_instance)
    mapper = orm.object_mapper(mapped_instance)
    path = []  # building the path helps avoid extra slashes and
    for name in relation.split('/'):
        if name.strip() != "":
            path.append(name)
            mapper = getattr(mapper.relationships, name).mapper

    # query the mapped class and the end point relation using the
    # list of the passed relations to create the join between the
    # two
    query = db.session.query(mapped_class, mapper.class_).\
        filter(getattr(mapped_class, 'id') == mapped_instance.id).\
        join(*path)

    return query.count()


def ilike(col, val, engine=None):
    """
    Return a cross platform ilike function.
    """
    import bauble.db as db
    from sqlalchemy import func
    if not engine:
        engine = db.engine
    if engine.name == 'postgresql':
        return col.op('ILIKE')(val)
    else:
        return func.lower(col).like(func.lower(val))
