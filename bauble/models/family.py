from sqlalchemy import (func, Column, Date, Enum, ForeignKey, Integer, String, Unicode,
                        UnicodeText, UniqueConstraint)
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.associationproxy import association_proxy

import bauble.db as db
import bauble.search as search


def family_markup_func(family):
    """
    return a string or object with __str__ method to use to markup
    text in the results view
    """
    return family

#
# Family
#
class Family(db.Model):
    """
    :Table name: family

    :Columns:
        *family*:
            The name if the family. Required.

        *qualifier*:
            The family qualifier.

            Possible values:
                * s. lat.: aggregrate family (senso lato)

                * s. str.: segregate family (senso stricto)

                * '': the empty string

        *notes*:
            Free text notes about the family.

    :Properties:
        *synonyms*:
            An association to _synonyms that will automatically
            convert a Family object and create the synonym.

    :Constraints:
        The family table has a unique constraint on family/qualifier.
    """
    __tablename__ = 'family'
    __table_args__ = (UniqueConstraint('family', 'qualifier'),)
    __mapper_args__ = {'order_by': ['Family.family', 'Family.qualifier']}

    # columns
    family = Column(String(45), nullable=False, index=True)

    # we use the blank string here instead of None so that the
    # contraints will work properly,
    qualifier = Column(Enum('s. lat.', 's. str.'))

    # relations
    synonyms = association_proxy('_synonyms', 'synonym')
    _synonyms = relation('FamilySynonym',
                         primaryjoin='Family.id==FamilySynonym.family_id',
                         cascade='all, delete-orphan', uselist=True,
                         backref='family')

    def __str__(self):
        return Family.str(self)

    @staticmethod
    def str(family, qualifier=False):
        if family.family is None:
            return repr(family)
        else:
            return ' '.join([s for s in [family.family, family.qualifier]
                             if s not in (None, '')])


class FamilyNote(db.Model):
    """
    Notes for the family table
    """
    __tablename__ = 'family_note'

    date = Column(Date, default=func.now())
    user = Column(Unicode(64))
    category = Column(Unicode(32))
    note = Column(UnicodeText, nullable=False)
    family_id = Column(Integer, ForeignKey('family.id'), nullable=False)
    family = relation('Family', uselist=False,
                      backref=backref('notes', cascade='all, delete-orphan'))


class FamilySynonym(db.Model):
    """
    :Table name: family_synonyms

    :Columns:
        *family_id*:

        *synonyms_id*:

    :Properties:
        *synonyms*:

        *family*:
    """
    __tablename__ = 'family_synonym'

    # columns
    family_id = Column(Integer, ForeignKey('family.id'), nullable=False)
    synonym_id = Column(Integer, ForeignKey('family.id'), nullable=False,
                        unique=True)

    # relations
    synonym = relation('Family', uselist=False,
                       primaryjoin='FamilySynonym.synonym_id==Family.id')

    def __init__(self, synonym=None, **kwargs):
        # it is necessary that the first argument here be synonym for
        # the Family.synonyms association_proxy to work
        self.synonym = synonym
        super(FamilySynonym, self).__init__(**kwargs)


    def __str__(self):
        return Family.str(self.synonym)


#
# setup the search matchers
#
mapper_search = search.get_strategy('MapperSearch')
mapper_search.add_meta(('families', 'family', 'fam'), Family, ['family'])
