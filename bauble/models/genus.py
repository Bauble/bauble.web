import xml

from sqlalchemy import (func, Column, Date, Enum, ForeignKey, Integer, String, Text,
                        UniqueConstraint)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

import bauble.db as db
import bauble.search as search
import bauble.utils as utils

# TODO: warn the user that a duplicate genus name is being entered
# even if only the author or qualifier is different

# TODO: should be a higher_taxon column that holds values into
# subgen, subfam, tribes etc, maybe this should be included in Genus

# TODO: since there can be more than one genus with the same name but
# different authors we need to show the Genus author in the result
# search, we should also check if when entering a plantname with a
# chosen genus if that genus has an author ask the user if they want
# to use the accepted name and show the author of the genus then so
# they aren't using the wrong version of the Genus, e.g. Cananga


def genus_markup_func(genus):
    '''
    '''
    # TODO: the genus should be italicized for markup
    return utils.xml_safe(genus), utils.xml_safe(genus.family)



class Genus(db.Model):
    """
    :Table name: genus

    :Columns:
        *genus*:
            The name of the genus.  In addition to standard generic
            names any additional hybrid flags or genera should included here.

        *qualifier*:
            Designates the botanical status of the genus.

            Possible values:
                * s. lat.: aggregrate genus (sensu lato)

                * s. str.: segregate genus (sensu stricto)

        *author*:
            The name or abbreviation of the author who published this genus.

    :Properties:
        *family*:
            The family of the genus.

        *synonyms*:
            The list of genera who are synonymous with this genus.  If
            a genus is listed as a synonym of this genus then this
            genus should be considered the current and valid name for
            the synonym.

    :Contraints:
        The combination of genus, author, qualifier
        and family_id must be unique.
    """

    __table_args__ = (UniqueConstraint('genus', 'author',
                                       'qualifier', 'family_id'),
                      {})
    __mapper_args__ = {'order_by': ['genus', 'author']}

    # columns
    genus = Column(String(64), nullable=False, index=True)

    # use '' instead of None so that the constraints will work propertly
    author = Column(String(255), default='')
    qualifier = Column(Enum('s. lat.', 's. str', ''))

    family_id = Column(Integer, ForeignKey('family.id'), nullable=False)
    family = relationship('Family', backref=backref('genera', cascade='all,delete-orphan'),
                          info={'dumpable': True})

    # relations
    synonyms = association_proxy('_synonyms', 'synonym')
    _synonyms = relationship('GenusSynonym',
                             primaryjoin='Genus.id==GenusSynonym.genus_id',
                             cascade='all, delete-orphan', uselist=True,
                             backref='genus')

    def __str__(self):
        return Genus.str(self)


    def str(self, *args, author=False):
        # TODO: the genus should be italicized for markup
        if self.genus is None:
            return repr(self)
        elif not author or self.author is None:

            return ' '.join([s for s in [self.genus, self.qualifier] if s not in ('', None)])
        else:
            return ' '.join(
                [s for s in [self.genus, self.qualifier,
                             xml.sax.saxutils.escape(self.author)] if s not in ('', None)])


class GenusNote(db.Model):
    """
    Notes for the genus table
    """
    __mapper_args__ = {'order_by': 'genus_note.date'}

    date = Column(Date, default=func.now())
    user = Column(String(64))
    category = Column(String(32))
    note = Column(Text, nullable=False)
    genus_id = Column(Integer, ForeignKey('genus.id'), nullable=False)
    genus = relationship('Genus', uselist=False,
                         backref=backref('notes', cascade='all, delete-orphan'))



class GenusSynonym(db.Model):
    """
    :Table name: genus_synonym
    """

    # columns
    genus_id = Column(Integer, ForeignKey('genus.id'), nullable=False)

    # a genus can only be a synonum of one other genus
    synonym_id = Column(Integer, ForeignKey('genus.id'), nullable=False,
                        unique=True)

    # relations
    synonym = relationship('Genus', uselist=False,
                           primaryjoin='GenusSynonym.synonym_id==Genus.id')


    def __init__(self, synonym=None, **kwargs):
        # it is necessary that the first argument here be synonym for
        # the Genus.synonyms association_proxy to work
        self.synonym = synonym
        super(GenusSynonym, self).__init__(**kwargs)


    def __str__(self):
        return str(self.synonym)


#  setup the search matches
mapper_search = search.get_strategy('MapperSearch')
mapper_search.add_meta(('genera', 'genus', 'gen'), Genus, ['genus'])
