from flask.ext.babel import gettext as _
from sqlalchemy import (func, Boolean, Column, Date, DateTime, Enum, Float, ForeignKey,
                        Integer, String, Text, UniqueConstraint)
from sqlalchemy.orm import backref, object_mapper, relationship

import bauble
import bauble.i18n
import bauble.db as db
from bauble.models.geography import Geography
#import bauble.utils as utils
#from bauble.utils.log import debug
import bauble.search as search

def coll_markup_func(coll):
    acc = coll.source.accession
    safe = utils.xml_safe_utf8
    return '%s - <small>%s</small>' %  \
        (safe(acc), safe(acc.taxon_str())), safe(coll)


class Source(db.Model):
    """
    """
    sources_code = Column(String(32))

    accession_id = Column(Integer, ForeignKey('accession.id'), unique=True)

    source_detail_id = Column(Integer, ForeignKey('source_detail.id'))
    source_detail = relationship('SourceDetail', uselist=False,
                                 backref=backref('sources',
                                                 cascade='all, delete-orphan'))

    collection = relationship('Collection', uselist=False,
                              cascade='all, delete-orphan',
                              backref=backref('source', uselist=False))

    # Relation to a propagation that is specific to this Source and
    # not attached to a Plant.
    propagation_id = Column(Integer, ForeignKey('propagation.id'))
    propagation = relationship("Propagation", foreign_keys=propagation_id,
                               cascade='all, delete-orphan', single_parent=True,
                               backref=backref('source', uselist=False))

    # relation to a Propagation that already exists and is attached
    # to a Plant
    plant_propagation_id = Column(Integer, ForeignKey('plant_prop.id'))
    plant_propagation = relationship("PlantPropagation", foreign_keys=plant_propagation_id,
                                     uselist=False)


    def json(self, *args, **kwargs):
        data = self.source_detail.json() if self.source_detail is not None else {}
        data['sources_code'] = self.sources_code
        data['collection'] = self.collection.json() if self.collection is not None else {}
        data['propagation'] = self.propagation.json() if self.propagation is not None else {}
        data['plant_propagation_id'] = self.plant_propagation.id if self.plant_propagation is not None else None
        return data



source_type_values = {
    'Expedition': _('Expedition'),
                      'GeneBank': _('Gene Bank'),
    'BG': _('Botanic Garden or Arboretum'),
    'Research/FieldStation': _('Research/Field Station'),
    'Staff': _('Staff member'),
    'UniversityDepartment': _('University Department'),
    'Club': _('Horticultural Association/Garden Club'),
    'MunicipalDepartment': _('Municipal department'),
    'Commercial': _('Nursery/Commercial'),
    'Individual': _('Individual'),
    'Other': _('Other'),
    'Unknown': _('Unknown')
}


class SourceDetail(db.Model):
    __tablename__ = 'source_detail'
    __mapper_args__ = {'order_by': 'name'}

    name = Column(String(75), unique=True)
    description = Column(Text)
    source_type = Column(Enum(*source_type_values.keys()))

    def __str__(self):
        return self.name if self.name else ""



# TODO: should provide a collection type: alcohol, bark, boxed,
# cytological, fruit, illustration, image, other, packet, pollen,
# print, reference, seed, sheet, slide, transparency, vertical,
# wood.....see HISPID standard, in general need to be more herbarium
# aware

# TODO: create a DMS column type to hold latitude and longitude,
# should probably store the DMS data as a string in decimal degrees
class Collection(db.Model):
    """
    :Table name: collection

    :Columns:
            *collector*: :class:`sqlalchemy.types.String`

            *collectors_code*: :class:`sqlalchemy.types.String`

            *date*: :class:`sqlalchemy.types.Date`

            *locale*: :class:`sqlalchemy.types.Text`

            *latitude*: :class:`sqlalchemy.types.Float`

            *longitude*: :class:`sqlalchemy.types.Float`

            *gps_datum*: :class:`sqlalchemy.types.String`

            *geo_accy*: :class:`sqlalchemy.types.Float`

            *elevation*: :class:`sqlalchemy.types.Float`

            *elevation_accy*: :class:`sqlalchemy.types.Float`

            *habitat*: :class:`sqlalchemy.types.Text`

            *geography_id*: :class:`sqlalchemy.types.Integer`

            *notes*: :class:`sqlalchemy.types.Text`

            *accession_id*: :class:`sqlalchemy.types.Integer`


    :Properties:


    :Constraints:
    """
    __tablename__ = 'collection'

    # columns
    collector = Column(String)
    collectors_code = Column(String)
    date = Column(Date)
    locale = Column(Text, nullable=False)
    latitude = Column(String(15))
    longitude = Column(String(15))
    gps_datum = Column(String(32))
    geo_accy = Column(Float)
    elevation = Column(Float)
    elevation_accy = Column(Float)
    habitat = Column(Text)
    notes = Column(Text)

    geography_id = Column(Integer, ForeignKey('geography.id'))
    region = relationship(Geography, uselist=False)

    source_id = Column(Integer, ForeignKey('source.id'), unique=True)

    def __str__(self):
        return _('Collection at %s') % (self.locale or repr(self))




# setup the search mapper
mapper_search = search.get_strategy('MapperSearch')
mapper_search.add_meta(('contacts', 'contact', 'contacts', 'person', 'org',
                        'source'), SourceDetail, ['name'])
mapper_search.add_meta(('collections', 'collection', 'col', 'coll'),
                       Collection, ['locale'])
