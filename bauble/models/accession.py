from marshmallow import fields
from sqlalchemy import (event, func, Boolean, Column, Date, Enum, ForeignKey, Integer,
                        String, Text, UniqueConstraint)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import (backref, object_mapper, reconstructor, relationship,
                            MapperExtension, EXT_CONTINUE)
from sqlalchemy.orm.session import object_session

import bauble.db as db
from bauble.models.taxon import Taxon
import bauble.search as search

prov_type_values = {
    'Wild': 'Wild',
    'Cultivated': 'Propagule of cultivated wild plant',
    'NotWild': "Not of wild source",
    'InsufficientData': "Insufficient Data",
    'Unknown': "Unknown"
}


wild_prov_status_values = {
    'WildNative': "Wild native",
    'WildNonNative': "Wild non-native",
    'CultivatedNative': "Cultivated native",
    'InsufficientData': "Insufficient Data",
    'Unknown': "Unknown"
}


recvd_type_values = {
    'ALAY': 'Air layer',
    'BBPL': 'Balled & burlapped plant',
    'BRPL': 'Bare root plant',
    'BUDC': 'Bud cutting',
    'BUDD': 'Budded',
    'BULB': 'Bulb',
    'CLUM': 'Clump',
    'CORM': 'Corm',
    'DIVI': 'Division',
    'GRAF': 'Graft',
    'LAYE': 'Layer',
    'PLNT': 'Plant',
    'PSBU': 'Pseudobulb',
    'RCUT': 'Rooted cutting',
    'RHIZ': 'Rhizome',
    'ROOC': 'Root cutting',
    'ROOT': 'Root',
    'SCIO': 'Scion',
    'SEDL': 'Seedling',
    'SEED': 'Seed',
    'SPOR': 'Spore',
    'SPRL': 'Sporeling',
    'TUBE': 'Tuber',
    'UNKN': 'Unknown',
    'URCU': 'Unrooted cutting',
    'BBIL': 'Bulbil',
    'VEGS': 'Vegetative spreading',
    'SCKR': 'Root sucker'
}


class Verification(db.Model):
    """
    :Table name: verification

    :Columns:
      verifier: :class:`sqlalchemy.types.String`
        The name of the person that made the verification.
      date: :class:`sqlalchemy.types.Date`
        The date of the verification
      reference: :class:`sqlalchemy.types.Text`
        The reference material used to make this verification
      level: :class:`sqlalchemy.types.Integer`
        Determines the level or authority of the verifier. If it is
        not known whether the name of the record has been verified by
        an authority, then this field should be None.

        Possible values:
            - 0: The name of the record has not been checked by any authority.
            - 1: The name of the record determined by comparison with
              other named plants.
            - 2: The name of the record determined by a taxonomist or by
              other competent persons using herbarium and/or library and/or
              documented living material.
            - 3: The name of the plant determined by taxonomist engaged in
              systematic revision of the group.
            - 4: The record is part of type gathering or propagated from
              type material by asexual methods

      notes: :class:`sqlalchemy.types.Text`
        Notes about this verification.
      accession_id: :class:`sqlalchemy.types.Integer`
        Foreign Key to the :class:`Accession` table.
      taxon_id: :class:`sqlalchemy.types.Integer`
        Foreign Key to the :class:`~bauble.plugins.plants.Taxon` table.
      prev_taxon_id: :class:`~sqlalchemy.types.Integer`
        Foreign key to the :class:`~bauble.plugins.plants.Taxon`
        table. What it was verified from.

    """
    __mapper_args__ = {'order_by': 'date'}

    # columns
    verifier = Column(String(64), nullable=False)
    date = Column(Date, nullable=False)
    reference = Column(Text)
    accession_id = Column(Integer, ForeignKey('accession.id'), nullable=False)

    # the level of assurance of this verification
    level = Column(Integer, nullable=False, autoincrement=False)

    # what it was verified as
    taxon_id = Column(Integer, ForeignKey('taxon.id'), nullable=False)

    # what it was verified from
    prev_taxon_id = Column(Integer, ForeignKey('taxon.id'), nullable=False)

    taxon = relationship('Taxon', primaryjoin='Verification.taxon_id==Taxon.id')
    prev_taxon = relationship('Taxon', primaryjoin='Verification.prev_taxon_id==Taxon.id')

    notes = Column(Text)



# TODO: auto add parent voucher if accession is a propagule of an
# existing accession and that parent accession has vouchers...or at
# least display them in the Voucher tab and Infobox
herbarium_codes = {}

class Voucher(db.Model):
    """
    :Table name: voucher

    :Columns:
      herbarium: :class:`sqlalchemy.types.String`
        The name of the herbarium.
      code: :class:`sqlalchemy.types.String`
        The herbarium code.
      parent_material: :class:`sqlalchemy.types.Boolean`
        Is this voucher the parent material of the accession.  E.g did
        the seed for the accession from come the plant used to make
        this voucher.
      accession_id: :class:`sqlalchemy.types.Integer`
        A foreign key to :class:`Accession`


    """
    herbarium = Column(String, nullable=False)
    code = Column(String(32), nullable=False)
    parent_material = Column(Boolean, default=False)
    accession_id = Column(Integer, ForeignKey('accession.id'), nullable=False)

    # accession  = relationship('Accession', uselist=False,
    #                       backref=backref('vouchers',
    #                                       cascade='all, delete-orphan'))


class AccessionNote(db.Model):
    """
    Notes for the accession table
    """
    __mapper_args__ = {'order_by': 'accession_note.date'}

    date = Column(Date, default=func.now())
    user = Column(String(64))
    category = Column(String(32))
    note = Column(Text, nullable=False)
    accession_id = Column(Integer, ForeignKey('accession.id'), nullable=False)
    accession = relationship('Accession', uselist=False,
                             backref=backref('notes', cascade='all, delete-orphan'))




# invalidate an accessions string cache after it has been updated
# class AccessionMapperExtension(MapperExtension):

#     def after_update(self, mapper, conn, instance):
#         instance.invalidate_str_cache()
#         return EXT_CONTINUE


class Accession(db.Model):
    """
    :Table name: accession

    :Columns:
        *code*: :class:`sqlalchemy.types.String`
            the accession code

        *prov_type*: :class:`bauble.types.Enum`
            the provenance type

            Possible values:
                * Wild:
                * Propagule of cultivated wild plant
                * Not of wild source
                * Insufficient Data
                * Unknown

        *wild_prov_status*:  :class:`bauble.types.Enum`
            wild provenance status, if prov_type is
            Wild then this column can be used to give more provenance
            information

            Possible values:
                * Wild native
                * Cultivated native
                * Insufficient Data
                * Unknown

        *date*: :class:`bauble.types.Date`
            the date this accession was accessioned


        *id_qual*: :class:`bauble.types.Enum`
            The id qualifier is used to indicate uncertainty in the
            identification of this accession

            Possible values:
                * aff. - affinity with
                * cf. - compare with
                * forsan - perhaps
                * near - close to
                * ? - questionable
                * incorrect

        *id_qual_rank*: :class:`sqlalchemy.types.String`
            The rank of the taxon that the id_qaul refers to.

        *private*: :class:`sqlalchemy.types.Boolean`
            Flag to indicate where this information is sensitive and
            should be kept private

        *taxon_id*: :class:`sqlalchemy.types.Integer()`
            foreign key to the taxon table

    :Properties:
        *taxon*:
            the taxon this accession refers to

        *source*:
            source is a relation to a Source instance

        *plants*:
            a list of plants related to this accession

        *verifications*:
            a list of verifications on the identification of this accession

    :Constraints:

    """
    __mapper_args__ = {'order_by': 'code'}

    @declared_attr
    def _additional_schema_fields(self):
        return {
            'taxon_str': fields.Function(lambda obj: obj.taxon_str(), dump_only=True)
        }

    # columns
    #: the accession code
    code = Column(String(20), nullable=False, unique=True)

    prov_type = Column(Enum(*prov_type_values.keys()))

    wild_prov_status = Column(Enum(*wild_prov_status_values.keys()))

    date_accd = Column(Date)
    date_recvd = Column(Date)
    quantity_recvd = Column(Integer, autoincrement=False)
    recvd_type = Column(Enum(*recvd_type_values.keys()))

    # "id_qual" new in 0.7
    id_qual = Column(Enum('aff.', 'cf.', 'incorrect', 'forsan', 'near', '?'))

    # new in 0.9, this column should contain the name of the column in
    # the taxon table that the id_qual refers to, e.g. genus, sp, etc.
    id_qual_rank = Column(String(10))

    # "private" new in 0.8b2
    private = Column(Boolean, default=False)
    taxon_id = Column(Integer, ForeignKey('taxon.id'), nullable=False)

    # intended location
    intended_location_id = Column(Integer, ForeignKey('location.id'))
    intended2_location_id = Column(Integer, ForeignKey('location.id'))

    # the source of the accession
    source = relationship('Source', uselist=False, cascade='all, delete-orphan',
                          backref=backref('accession', uselist=False))

    # relations
    taxon = relationship('Taxon', uselist=False,
                         backref=backref('accessions', cascade='all, delete-orphan'),)

    # use Plant.code for the order_by to avoid ambiguous column names
    plants = relationship('Plant', cascade='all, delete-orphan',
                          #order_by='plant.code',
                          backref=backref('accession', uselist=False))
    verifications = relationship('Verification',  # order_by='date',
                                 cascade='all, delete-orphan',
                                 backref=backref('accession', uselist=False))
    vouchers = relationship('Voucher', cascade='all, delete-orphan',
                            backref=backref('accession', uselist=False))
    intended_location = relationship('Location',
                                     primaryjoin='Accession.intended_location_id==Location.id')
    intended2_location = relationship('Location',
                                      primaryjoin='Accession.intended2_location_id==Location.id')

    def __init__(self, *args, **kwargs):
        self.__cached_taxon_str = {}
        super().__init__(*args, **kwargs)


    @reconstructor
    def init_on_load(self):
        """
        Called instead of __init__() when an Accession is loaded from
        the database.
        """
        self.__cached_taxon_str = {}


    def invalidate_str_cache(self):
        self.__cached_taxon_str = {}


    def __str__(self):
        return str(self.code) if self.code is not None else ''


    def taxon_str(self, authors=False, markup=False):
        """
        Return the string of the taxon with the id qualifier(id_qual)
        injected into the proper place.

        If the taxon isn't part of a session of if the taxon is dirty,
        i.e. in object_session(taxon).dirty, then a new string will be
        built even if the taxon hasn't been changeq since the last call
        to this method.
        """
        # WARNING: don't use session.is_modified() here because it
        # will query lots of dependencies
        try:
            cached = self.__cached_taxon_str[(markup, authors)]
        except KeyError:
            self.__cached_taxon_str[(markup, authors)] = None
            cached = None

        session = object_session(self.taxon)
        if session:
            # if not part of a session or if the taxon is dirty then
            # build a new string
            if cached is not None and self.taxon not in session.dirty:
                return cached
        if not self.taxon:
            return None


        #
        # TODO: this warning is left over from bauble.class.  it should probably be handled
        # in bauble.web one way or another
        #
        # show a warning if the id_qual is aff. or cf. but the
        # id_qual_rank is None, but only show it once
        # try:
        #     self.__warned_about_id_qual
        # except AttributeError:
        #     self.__warned_about_id_qual = False
        # if self.id_qual in ('aff.', 'cf.') and not self.id_qual_rank \
        #         and not self.__warned_about_id_qual:
        #     msg = _('If the id_qual is aff. or cf. '
        #             'then id_qual_rank is required. %s ' % self.code)
        #     warning(msg)
        #     self.__warned_about_id_qual = True

        # copy the taxon so we don't affect the original
        taxon = Taxon()
        taxon.genus = self.taxon.genus#session.query(Genus).get(self.taxon.genus_id);
        for col in object_mapper(self.taxon).local_table.c:
            setattr(taxon, col.name, getattr(self.taxon, col.name))

        del taxon.id

        # generate the string
        if self.id_qual in ('aff.', 'cf.'):
            if self.id_qual_rank == 'infrasp':
                taxon.sp = '%s %s' % (taxon.sp, self.id_qual)
            elif self.id_qual_rank:
                setattr(taxon, self.id_qual_rank,
                        '%s %s' % (self.id_qual,
                                   getattr(taxon, self.id_qual_rank)))

            sp_str = Taxon.str(taxon, authors, markup)
        elif self.id_qual:
            sp_str = '%s(%s)' % (Taxon.str(taxon, authors, markup),
                                 self.id_qual)
        else:
            sp_str = Taxon.str(taxon, authors, markup)

        # kill our temporary taxon
        del taxon

        self.__cached_taxon_str[(markup, authors)] = sp_str
        return sp_str


    def markup(self):
        return '%s (%s)' % (self.code, self.taxon.markup())


@event.listens_for(Accession, 'after_update')
def accession_after_upload(mapper, connection, target):
    target.invalidate_str_cache()


# setup the search matcher
mapper_search = search.get_strategy('MapperSearch')
mapper_search.add_meta(('accessions', 'accession', 'acc'), Accession, ['code'])
