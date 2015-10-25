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
