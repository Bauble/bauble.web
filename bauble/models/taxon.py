from itertools import chain

from flask.ext.babel import gettext as _, ngettext as _n
from sqlalchemy import (func, Boolean, Column, Date, Enum, ForeignKey, Integer, String,
                        Text, UniqueConstraint)
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.associationproxy import association_proxy

import bauble.db as db
import bauble.search as search


class VNList(list):
    """
    A Collection class for Taxon.vernacular_names

    This makes it possible to automatically remove a
    default_vernacular_name if the vernacular_name is removed from the
    list.
    """
    def remove(self, vn):
        super(VNList, self).remove(vn)
        try:
            if vn.taxon.default_vernacular_name == vn:
                del vn.taxon.default_vernacular_name
        except Exception as e:
            debug(e)


infrasp_rank_values = {
    'subsp.': _('subsp.'),
    'var.': _('var.'),
    'subvar.': _('subvar'),
    'f.': _('f.'),
    'subf.': _('subf.'),
    'cv.': _('cv.')
}

# TODO: there is a trade_name column but there's no support yet for editing
# the trade_name or for using the trade_name when building the string
# for the taxon, for more information about trade_names see,
# http://www.hortax.org.uk/gardenplantsnames.html

# TODO: the specific epithet should not be non-nullable but instead
# make sure that at least one of the specific epithet, cultivar name
# or cultivar group is specificed

class Taxon(db.Model):
    """
    :Table name: taxon

    :Columns:
        *sp*:
        *sp2*:
        *sp_author*:

        *hybrid*:
            Hybrid flag

        *infrasp1*:
        *infrasp1_rank*:
        *infrasp1_author*:

        *infrasp2*:
        *infrasp2_rank*:
        *infrasp2_author*:

        *infrasp3*:
        *infrasp3_rank*:
        *infrasp3_author*:

        *infrasp4*:
        *infrasp4_rank*:
        *infrasp4_author*:

        *cv_group*:
        *trade_name*:

        *sp_qual*:
            Taxon qualifier

            Possible values:
                *agg.*: An aggregate taxon

                *s. lat.*: aggregrate taxon (sensu lato)

                *s. str.*: segregate taxon (sensu stricto)

        *label_distribution*:
            Text
            This field is optional and can be used for the label in case
            str(self.distribution) is too long to fit on the label.

    :Properties:
        *accessions*:

        *vernacular_names*:

        *default_vernacular_name*:

        *synonyms*:

        *distribution*:

    :Constraints:
        The combination of sp, sp_author, hybrid, sp_qual,
        cv_group, trade_name, genus_id
    """
    __mapper_args__ = {'order_by': ['sp', 'sp_author']}

    # columns
    sp = Column(String(64), index=True)
    sp2 = Column(String(64), index=True)  # in case hybrid=True
    sp_author = Column(String(128))
    hybrid = Column(Boolean, default=False)
    sp_qual = Column(Enum('agg.', 's. lat.', 's. str.'))
    cv_group = Column(String(50))
    trade_name = Column(String(64))

    infrasp1 = Column(String(64))
    infrasp1_rank = Column(Enum(*infrasp_rank_values.keys()))
    infrasp1_author = Column(String(64))

    infrasp2 = Column(String(64))
    infrasp2_rank = Column(Enum(*infrasp_rank_values.keys()))
    infrasp2_author = Column(String(64))

    infrasp3 = Column(String(64))
    infrasp3_rank = Column(Enum(*infrasp_rank_values.keys()))
    infrasp3_author = Column(String(64))

    infrasp4 = Column(String(64))
    infrasp4_rank = Column(Enum(*infrasp_rank_values.keys()))
    infrasp4_author = Column(String(64))

    genus_id = Column(Integer, ForeignKey('genus.id'), nullable=False)

    label_distribution = Column(Text)

    # relations
    synonyms = association_proxy('_synonyms', 'synonym')
    _synonyms = relation('TaxonSynonym',
                         primaryjoin='Taxon.id==TaxonSynonym.taxon_id',
                         cascade='all, delete-orphan', uselist=True,
                         backref='taxon')


    vernacular_names = relation('VernacularName', cascade='all, delete-orphan',
                                collection_class=VNList,
                                backref=backref('taxon', uselist=False))
    _default_vernacular_name = relation('DefaultVernacularName', uselist=False,
                                        cascade='all, delete-orphan',
                                        backref=backref('taxon', uselist=False))
    distribution = relation('TaxonDistribution',
                            cascade='all, delete-orphan',
                            backref=backref('taxon', uselist=False))

    habit_id = Column(Integer, ForeignKey('habit.id'), default=None)
    habit = relation('Habit', uselist=False, backref='taxa')

    flower_color_id = Column(Integer, ForeignKey('color.id'), default=None)
    flower_color = relation('Color', uselist=False, backref='taxa')

    #hardiness_zone = Column(String(4))

    awards = Column(Text)

    def __init__(self, *args, **kwargs):
        super(Taxon, self).__init__(*args, **kwargs)

    def __str__(self):
        '''
        returns a string representation of this taxon,
        calls Taxon.str(self)
        '''
        return Taxon.str(self)

    def _get_default_vernacular_name(self):
        if self._default_vernacular_name is None:
            return None
        return self._default_vernacular_name.vernacular_name

    def _set_default_vernacular_name(self, vn):
        if vn is None:
            del self.default_vernacular_name
            return
        if vn not in self.vernacular_names:
            self.vernacular_names.append(vn)
        d = DefaultVernacularName()
        d.vernacular_name = vn
        self._default_vernacular_name = d

    def _del_default_vernacular_name(self):
        utils.delete_or_expunge(self._default_vernacular_name)
        del self._default_vernacular_name
    default_vernacular_name = property(_get_default_vernacular_name,
                                       _set_default_vernacular_name,
                                       _del_default_vernacular_name)

    def distribution_str(self):
        if self.distribution is None:
            return ''
        else:
            dist = ['%s' % d for d in self.distribution]
            return unicode(', ').join(sorted(dist))


    def markup(self, authors=False):
        '''
        returns this object as a string with markup

        :param authors: flag to toggle whethe the author names should be
        included
        '''
        return Taxon.str(self, authors, True)


    # in PlantPlugins.init() we set this to 'x' for win32
    hybrid_char = '\u2a09'  # U+2A09

    @staticmethod
    def str(taxon, authors=False, markup=False):
        '''
        returns a string for taxon

        :param taxon: the taxon object to get the values from
        :param authors: flags to toggle whether the author names should be
        included
        :param markup: flags to toggle whether the returned text is marked up
        to show italics on the epithets
        '''
        # TODO: this method will raise an error if the session is none
        # since it won't be able to look up the genus....we could
        # probably try to query the genus directly with the genus_id
        genus = str(taxon.genus)
        sp = taxon.sp
        sp2 = taxon.sp2
        if markup:
            # escape = utils.xml_safe_utf8
            escape = str  # from bauble2 conversion
            italicize = lambda s: '<i>%s</i>' % escape(s)
            genus = italicize(genus)
            if sp is not None:
                sp = italicize(taxon.sp)
            if sp2 is not None:
                sp2 = italicize(taxon.sp2)
        else:
            italicize = lambda s: '%s' % s
            escape = lambda x: x

        author = None
        if authors and taxon.sp_author:
            author = escape(taxon.sp_author)

        infrasp = ((taxon.infrasp1_rank, taxon.infrasp1,
                    taxon.infrasp1_author),
                   (taxon.infrasp2_rank, taxon.infrasp2,
                    taxon.infrasp2_author),
                   (taxon.infrasp3_rank, taxon.infrasp3,
                    taxon.infrasp3_author),
                   (taxon.infrasp4_rank, taxon.infrasp4,
                    taxon.infrasp4_author))

        infrasp_parts = []
        group_added = False
        for rank, epithet, iauthor in infrasp:
            if rank == 'cv.' and epithet:
                if taxon.cv_group and not group_added:
                    group_added = True
                    infrasp_parts.append(_("(%(group)s Group)") % \
                                             dict(group=taxon.cv_group))
                infrasp_parts.append("'%s'" % escape(epithet))
            else:
                if rank:
                    infrasp_parts.append(rank)
                if epithet and rank:
                    infrasp_parts.append(italicize(epithet))
                elif epithet:
                    infrasp_parts.append(escape(epithet))

            if authors and iauthor:
                infrasp_parts.append(escape(iauthor))
        if taxon.cv_group and not group_added:
            infrasp_parts.append(_("%(group)s Group") % \
                                     dict(group=taxon.cv_group))

        # create the binomial part
        binomial = []
        if taxon.hybrid:
            if taxon.sp2:
                binomial = [genus, sp, taxon.hybrid_char, sp2, author]
            else:
                binomial = [genus, taxon.hybrid_char, sp, author]
        else:
            binomial = [genus, sp, sp2, author]

        # create the tail a.k.a think to add on to the end
        tail = []
        if taxon.sp_qual:
            tail = [taxon.sp_qual]

        parts = chain(binomial, infrasp_parts, tail)
        s = ' '.join(filter(lambda x: x not in ('', None), parts))
        return s


    infrasp_attr = {1: {'rank': 'infrasp1_rank',
                        'epithet': 'infrasp1',
                        'author': 'infrasp1_author'},
                    2: {'rank': 'infrasp2_rank',
                        'epithet': 'infrasp2',
                        'author': 'infrasp2_author'},
                    3: {'rank': 'infrasp3_rank',
                        'epithet': 'infrasp3',
                        'author': 'infrasp3_author'},
                    4: {'rank': 'infrasp4_rank',
                        'epithet': 'infrasp4',
                        'author': 'infrasp4_author'}}


    def get_infrasp(self, level):
        """
        level should be 1-4
        """
        return getattr(self, self.infrasp_attr[level]['rank']), \
            getattr(self, self.infrasp_attr[level]['epithet']), \
            getattr(self, self.infrasp_attr[level]['author'])


    def set_infrasp(self, level, rank, epithet, author=None):
        """
        level should be 1-4
        """
        setattr(self, self.infrasp_attr[level]['rank'], rank)
        setattr(self, self.infrasp_attr[level]['epithet'], epithet)
        setattr(self, self.infrasp_attr[level]['author'], author)



class TaxonNote(db.Model):
    """
    Notes for the taxon table
    """
    __mapper_args__ = {'order_by': 'taxon_note.date'}

    date = Column(Date, default=func.now())
    user = Column(String(64))
    category = Column(String(32))
    note = Column(Text, nullable=False)
    taxon_id = Column(Integer, ForeignKey('taxon.id'), nullable=False)
    taxon = relation('Taxon', uselist=False,
                     backref=backref('notes', cascade='all, delete-orphan'))



class TaxonSynonym(db.Model):
    """
    :Table name: taxon_synonym
    """

    # columns
    taxon_id = Column(Integer, ForeignKey('taxon.id'),
                      nullable=False)
    synonym_id = Column(Integer, ForeignKey('taxon.id'),
                        nullable=False, unique=True)

    # relations
    synonym = relation('Taxon', uselist=False,
                       primaryjoin='TaxonSynonym.synonym_id==Taxon.id')

    def __init__(self, synonym=None, **kwargs):
        # it is necessary that the first argument here be synonym for
        # the Taxon.synonyms association_proxy to work
        self.synonym = synonym
        super(TaxonSynonym, self).__init__(**kwargs)


    def __str__(self):
        return str(self.synonym)



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
    vernacular_name = relation(VernacularName, uselist=False)

    def __str__(self):
        return str(self.vernacular_name)



class TaxonDistribution(db.Model):
    """
    :Table name: taxon_distribution

    :Columns:

    :Properties:

    :Constraints:
    """

    # columns
    geography_id = Column(Integer, ForeignKey('geography.id'), nullable=False)
    taxon_id = Column(Integer, ForeignKey('taxon.id'), nullable=False)


    def json(self, pick=None):
        return self.geography.json()


    def __str__(self):
        return str(self.geography)




# late bindings
TaxonDistribution.geography = relation('Geography',
                primaryjoin='TaxonDistribution.geography_id==Geography.id',
                                         uselist=False)

class Habit(db.Model):
    name = Column(String(64))
    code = Column(String(8), unique=True)

    def __str__(self):
        if self.name:
            return '%s (%s)' % (self.name, self.code)
        else:
            return str(self.code)


class Color(db.Model):
    name = Column(String(32))
    code = Column(String(8), unique=True)

    def __str__(self):
        if self.name:
            return '%s (%s)' % (self.name, self.code)
        else:
            return str(self.code)



# setup search matcher
mapper_search = search.get_strategy('MapperSearch')
mapper_search.add_meta(('taxa', 'taxon', 'sp'), Taxon,
                       ['sp', 'sp2', 'infrasp1', 'infrasp2',
                        'infrasp3', 'infrasp4'])
mapper_search.add_meta(('vernacular', 'vern', 'common'),
                       VernacularName, ['name'])
