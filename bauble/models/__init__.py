from sqlalchemy import func, inspect, schema, Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base, declared_attr
import sqlalchemy.orm as orm

# from bauble.types import DateTime
import bauble.db as db

def get_relation(model, model_id, path, session=None):
    mapper = orm.class_mapper(model)
    if isinstance(path, str):
        path = path.split('.')
    for name in path:
        relationship = mapper.relationships[name]
        mapper = relationship.mapper

    local_session = False if session else True
    if not session:
        session = db.Session()

    result = session.query(model, mapper.class_)\
        .filter(model.id == model_id)\
        .join(*path).all()

    if local_session:
        session.close()

    # if its a scalar return it as a scalar else return it as a list
    if relationship.uselist:
        return [r[1] for r in result]
    else:
        return result[0][1] if len(result) > 0 else None


class ModelBase:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(True), server_default=func.now())
    updated_at = Column(DateTime(True), server_default=func.now(),
                        onupdate=func.now())

    # the default set of columns to show for json()
    json_default = set()

    # properties to never show for json() even if picked
    json_never = set()

    # the set of columns to omit by default for json()
    json_omit = set()

    # the union of json_never and json_omit
    _default_omit = set()

    def __new__(cls, *args, **kwargs):
        # TODO: we should build the omit once when the class is declared rather
        # than evertime it's instantiated

        cls._default_omit = cls.json_omit | {key for key in inspect(cls).attrs.keys() if key.startswith('_') or key in cls.json_never}
        return super().__new__(cls)


    # Return a dict that can be safely serialized to json.dumps()
    def json(self, pick=None):
        # TODO: we need to get all attributes, not just columns, i.e. handling
        # embedding with pick
        columns = set(inspect(self).mapper.columns.keys())
        if pick:
            columns = columns.intersection(pick).difference(self.never)
        else:
            columns = columns.difference(self._default_omit)

        data = {col: getattr(self, col) for col in columns}
        if (pick and 'str' in pick) or 'str' not in self._default_omit:
            data['str'] = str(self)

        return data


    def set_attributes(self, dict_):
        for key, value in dict_.items():
            setattr(self, key, value)



Model = declarative_base(cls=ModelBase)

system_metadata = schema.MetaData()
SystemModel = declarative_base(cls=ModelBase, metadata=system_metadata)
"""SystemModel is the base mapper for system level tables.  Any tables using
base will only be created once in the database and won't be attached to an
organization's schema.
"""

# import bauble.model.meta
from bauble.models.geography import Geography
from bauble.models.family import Family, FamilyNote, FamilySynonym
from bauble.models.genus import Genus, GenusNote
from bauble.models.taxon import Taxon, TaxonDistribution, TaxonNote, TaxonSynonym, VernacularName
from bauble.models.accession import Accession, AccessionNote
from bauble.models.plant import Plant, PlantChange
from bauble.models.location import Location
from bauble.models.source import Source, SourceDetail, Collection
from bauble.models.propagation import Propagation, PlantPropagation, PropRooted, PropCutting, PropSeed
from bauble.models.report import Report

from bauble.models.user import User
from bauble.models.organization import Organization
from bauble.models.invitation import Invitation
