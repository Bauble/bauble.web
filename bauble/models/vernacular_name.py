from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

import bauble.db as db
import bauble.search as search

class VernacularName(db.Model):
    """
    :Table name: vernacular_name

    :Columns:
        *name*:
            the vernacular name

        *language*:
            language is free text and could include something like UK
            or US to identify the origin of the name

        *taxon_id*:
            key to the taxon this vernacular name refers to

    :Properties:

    :Constraints:
    """
    name = Column(String(128), nullable=False)
    language = Column(String(128))
    taxon_id = Column(Integer, ForeignKey('taxon.id'), nullable=False)
    __table_args__ = (UniqueConstraint('name', 'language',
                                       'taxon_id', name='vn_index'), {})

    def __str__(self):
        if self.name:
            return self.name
        else:
            return ''



mapper_search = search.get_strategy('MapperSearch')
mapper_search.add_meta(('vernacular', 'vern', 'common'),
                       VernacularName, ['name'])
