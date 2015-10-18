from datetime import datetime
import re
import sys

from attrdict import AttrDict
import bcrypt
from flask.ext.sqlalchemy import (SQLAlchemy, Model as ExtModel, _BoundDeclarativeMeta,
                                  _QueryProperty)
from flask.ext.migrate import Migrate
from flask_marshmallow import Marshmallow
from sqlalchemy import func, Column, DateTime, Integer, MetaData
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.hybrid import Comparator


ma = Marshmallow()

class Schema(ma.Schema):

    def make_object(self, data):
        return AttrDict(**data)


class _Model(ExtModel):

    """
    The default Model base class.
    """

    @declared_attr
    def __tablename__(cls):
        # return underscore cased class name
        return re.sub('(?!^)([A-Z]+)', r'_\1', cls.__name__).lower()

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(True), server_default=func.now())
    updated_at = Column(DateTime(True), server_default=func.now(),
                        onupdate=func.now())


class DBPlugin(SQLAlchemy):

    metadata = MetaData()

    def init_app(self, app):
        super().init_app(app)
        # TODO: we're not using a db uet
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get('DATABASE_URL')
        ma.init_app(app)
        Migrate(app, self)


    def make_declarative_base(self):
        """Creates the declarative base."""
        base = declarative_base(cls=_Model, name='Model', metadata=self.metadata,
                                metaclass=_BoundDeclarativeMeta)
        base.query = _QueryProperty(self)
        return base


plugin = DBPlugin()
plugin.ma = plugin.marshmallow = ma
plugin.Schema = Schema
sys.modules[__name__] = plugin
