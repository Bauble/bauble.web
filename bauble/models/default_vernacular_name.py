from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

import bauble.db as db

class DefaultVernacularName(db.Model):
    """
    :Table name: default_vernacular_name

    DefaultVernacularName is not meant to be instantiated directly.
    Usually the default vernacular name is set on a taxon by setting
    the default_vernacular_name property on Taxon to a
    VernacularName instance

    :Columns:
        *id*:
            Integer, primary_key

        *taxon_id*:
            foreign key to taxon.id, nullable=False

        *vernacular_name_id*:

    :Properties:

    :Constraints:
    """
    __table_args__ = (UniqueConstraint('taxon_id', 'vernacular_name_id',
                                       name='default_vn_index'), {})

    # columns
    taxon_id = Column(Integer, ForeignKey('taxon.id'), nullable=False)
    vernacular_name_id = Column(Integer, ForeignKey('vernacular_name.id'),
                                nullable=False)

    # relations
    vernacular_name = relationship('VernacularName', uselist=False)

    def __str__(self):
        return str(self.vernacular_name)
