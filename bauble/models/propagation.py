import datetime

from flask.ext.babel import gettext as _
from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import backref, relationship
from sqlalchemy.exc import DBAPIError

import bauble
import bauble.db as db
from bauble.error import CommitException


prop_type_values = {
    'Seed': _("Seed"),
    'UnrootedCutting': _('Unrooted cutting'),
    'Other': _('Other')
}

class PlantPropagation(db.Model):
    """
    PlantPropagation provides an intermediate relation from
    Plant->Propagation
    """
    plant_id = Column(Integer, ForeignKey('plant.id'), nullable=False)
    propagation_id = Column(Integer, ForeignKey('propagation.id'),
                            nullable=False)

    propagation = relationship('Propagation', uselist=False)
    plant = relationship('Plant', uselist=False)


    def json(self, depth=1):
        """
        """
        d = self.propagation.json(depth)
        d['ref'] = '/plant/' + str(self.plant_id) + d['ref]']
        return d



class Propagation(db.Model):
    """
    Propagation
    """
    #recvd_as = Column(String(10)) # seed, urcu, other

    prop_type = Column(Enum(*prop_type_values.keys()), nullable=False)

    notes = Column(Text)
    date = Column(Date)

    cutting = relationship('PropCutting',
                           primaryjoin='Propagation.id==PropCutting.propagation_id',
                           cascade='all,delete-orphan', uselist=False,
                           backref=backref('propagation', uselist=False))

    seed = relationship('PropSeed',
                        primaryjoin='Propagation.id==PropSeed.propagation_id',
                        cascade='all,delete-orphan', uselist=False,
                        backref=backref('propagation', uselist=False))


    def _get_details(self):
        if self.prop_type == 'Seed':
            return self.seed
        elif self.prop_type == 'UnrootedCutting':
            return self.cutting
        elif self.notes:
            return self.notes
        else:
            raise NotImplementedError

    def _set_details(self, details):
        """
        The details param is a dictionary of properties for either the PropCutting or PropSeed
        depenging on the property type.
        """
        if self.prop_type == 'Seed':
            self.cutting = None
            if self.seed is None:
                self.seed = PropSeed()
            self.seed.set_attributes(details)
        elif self.prop_type == 'UnrootedCutting':
            self.seed = None
            if self.cutting is None:
                self.cutting = PropCutting()
            self.cutting.set_attributes(details)
        elif self.prop_type != 'Other':
            raise ValueError("Unknown propagation type: {}".format(self.prop_type))

    details = property(_get_details, _set_details)

    def get_summary(self):
        """
        """
        # TODO: need a date format string from the settings
        # date_format = prefs.prefs[prefs.date_format_pref]
        date_format = '%d-%m-%Y'

        def get_date(date):
            if isinstance(date, datetime.date):
                return date.strftime(date_format)
            return date

        s = str(self)
        if self.prop_type == 'UnrootedCutting':
            c = self.cutting
            values = []
            if c.cutting_type is not None:
                values.append(_('Cutting type: %s') %
                              cutting_type_values[c.cutting_type])
            if c.length:
                values.append(_('Length: %(length)s%(unit)s') %
                              dict(length=c.length,
                                   unit=length_unit_values[c.length_unit]))
            if c.tip:
                values.append(_('Tip: %s') % tip_values[c.tip])
            if c.leaves:
                s = _('Leaves: %s') % leaves_values[c.leaves]
                if c.leaves == 'Removed' and c.leaves_reduced_pct:
                    s.append('(%s%%)' % c.leaves_reduced_pct)
                values.append(s)
            if c.flower_buds:
                values.append(_('Flower buds: %s') %
                              flower_buds_values[c.flower_buds])
            if c.wound is not None:
                values.append(_('Wounded: %s' % wound_values[c.wound]))
            if c.fungicide:
                values.append(_('Fungal soak: %s' % c.fungicide))
            if c.hormone:
                values.append(_('Hormone treatment: %s' % c.hormone))
            if c.bottom_heat_temp:
                values.append(_('Bottom heat: %(temp)s%(unit)s') %
                              dict(temp=c.bottom_heat_temp,
                                   unit=bottom_heat_unit_values[c.bottom_heat_unit]))
            if c.container:
                values.append(_('Container: %s' % c.container))
            if c.media:
                values.append(_('Media: %s' % c.media))
            if c.location:
                values.append(_('Location: %s' % c.location))
            if c.cover:
                values.append(_('Cover: %s' % c.cover))

            if c.rooted_pct:
                values.append(_('Rooted: %s%%') % c.rooted_pct)
            s = ', '.join(values)
        elif self.prop_type == 'Seed':
            s = str(self)
            seed = self.seed
            values = []
            if seed.pretreatment:
                values.append(_('Pretreatment: %s') % seed.pretreatment)
            if seed.nseeds:
                values.append(_('# of seeds: %s') % seed.nseeds)
            date_sown = get_date(seed.date_sown)
            if date_sown:
                values.append(_('Date sown: %s') % date_sown)
            if seed.container:
                values.append(_('Container: %s') % seed.container)
            if seed.media:
                values.append(_('Media: %s') % seed.media)
            if seed.covered:
                values.append(_('Covered: %s') % seed.covered)
            if seed.location:
                values.append(_('Location: %s') % seed.location)
            germ_date = get_date(seed.germ_date)
            if germ_date:
                values.append(_('Germination date: %s') % germ_date)
            if seed.nseedlings:
                values.append(_('# of seedlings: %s') % seed.nseedlings)
            if seed.germ_pct:
                values.append(_('Germination rate: %s%%') % seed.germ_pct)
            date_planted = get_date(seed.date_planted)
            if date_planted:
                values.append(_('Date planted: %s') % date_planted)
            s = ', '.join(values)
        elif self.notes:
            s = utils.utf8(self.notes)

        return s


    def json(self, depth=1):
        d = dict(ref="/propagation/" + str(self.id))
        if depth > 0:
            d['prop_type'] = self.prop_type
            if self.prop_type == 'UnrootedCutting':
                d.update(self._json_cutting(depth))
            elif self.prop_type == 'Seed':
                d.update(self._json_seed(depth))


    def _json_cutting(self, depth):
        d = dict()
        d['cutting_type'] = self.cutting.cutting_type
        d['tip'] = self.cutting.tip
        d[' leaves'] = self.cutting.leaves
        d['leaves_reduced_pct'] = self.cutting.leaves_reduced_pct
        d['length'] = self.cutting.length
        d['length_unit'] = self.cutting.length_unit

        # single/double/slice
        d['wound'] = self.cutting.wound

        # removed/None
        d['flower_buds'] = self.cutting.flower_buds

        d['fungicide'] = self.cutting.fungicide  # fungal soak
        d['hormone'] = self.cutting.hormone  # powder/liquid/None....solution

        d['media'] = self.cutting.media
        d['container'] = self.cutting.container
        d['location'] = self.cutting.location
        d['cover'] = self.cutting.cover  # vispore, poly, plastic dome, poly bag

        d['bottom_heat_temp'] = self.cutting.bottom_heat_temp  # temperature of bottom heat

        # F/C
        d['bottom_heat_unit'] = self.cutting.bottom_heat_unit
        d['rooted_pct'] = self.cutting.rooted_pct

        d['rooted'] = []
        for rooted in self.cutting.rooted:
            d['rooted'].append(dict(date=rooted.date, quantity=rooted.quantity))

        return d


    def _json_seed(self, depth):
        d = dict()
        d['pretreatment'] = self.seed.pretreatment
        d['nseeds'] = self.seed.nseeds
        d['date_sown'] = self.seed.date_sown
        d['container'] = self.seed.container
        d['media'] = self.seed.media
        d['covered'] = self.seed.covered
        d['location'] = self.seed.location
        d['moved_from'] = self.seed.moved_from
        d['moved_to'] = self.seed.moved_to
        d['moved_date'] = self.seed.moved_date
        d['germ_date'] = self.seed.germ_date
        d['nseedlings'] = self.seed.nseedlings
        d['germ_pct'] = self.seed.germ_pct
        d['date_planted'] = self.seed.date_planted
        return d



class PropRooted(db.Model):
    """
    Rooting dates for cutting
    """
    __mapper_args__ = {'order_by': 'date'}

    date = Column(Date)
    quantity = Column(Integer, autoincrement=False)
    cutting_id = Column(Integer, ForeignKey('prop_cutting.id'), nullable=False)



cutting_type_values = {
    'Nodal': _('Nodal'),
    'InterNodal': _('Internodal'),
    'Other': _('Other')
}

tip_values = {
    'Intact': _('Intact'),
    'Removed': _('Removed'),
    'None': _('None')
}

leaves_values = {
    'Intact': _('Intact'),
    'Removed': _('Removed'),
    'None': _('None')
}

flower_buds_values = {
    'Removed': _('Removed'),
    'None': _('None')
}

wound_values = {
    'No': _('No'),
    'Single': _('Singled'),
    'Double': _('Double'),
    'Slice': _('Slice')
}


hormone_values = {
    'Liquid': _('Liquid'),
    'Powder': _('Powder'),
    'No': _('No')
}

bottom_heat_unit_values = {
    'F': _('\302\260F'),
    'C': _('\302\260C')
}

length_unit_values = {
    'mm': _('mm'),
    'cm': _('cm'),
    'in': _('in')
}


class PropCutting(db.Model):
    """
    A cutting
    """
    cutting_type = Column(Enum(*cutting_type_values.keys()), default='Other')
    tip = Column(Enum(*tip_values.keys()))
    leaves = Column(Enum(*leaves_values.keys()))
    leaves_reduced_pct = Column(Integer, autoincrement=False)
    length = Column(Integer, autoincrement=False)
    length_unit = Column(Enum(*length_unit_values.keys()))

    # single/double/slice
    wound = Column(Enum(*wound_values.keys()))

    # removed/None
    flower_buds = Column(Enum(*flower_buds_values.keys()))

    fungicide = Column(String) # fungal soak
    hormone = Column(String) # powder/liquid/None....solution

    media = Column(String)
    container = Column(String)
    location = Column(String)
    cover = Column(String) # vispore, poly, plastic dome, poly bag

    bottom_heat_temp = Column(Integer, autoincrement=False) # temperature of bottom heat

    # TODO: make the bottom heat unit required if bottom_heat_temp is
    # not null

    # F/C
    bottom_heat_unit = Column(Enum(*bottom_heat_unit_values.keys()))

    rooted_pct = Column(Integer, autoincrement=False)
    #aftercare = Column(Text) # same as propgation.notes

    propagation_id = Column(Integer, ForeignKey('propagation.id'),
                            nullable=False)

    rooted = relationship('PropRooted', cascade='all,delete-orphan',
                          backref=backref('cutting', uselist=False))


class PropSeed(db.Model):
    """
    """
    pretreatment = Column(Text)
    nseeds = Column(Integer, nullable=False, autoincrement=False)
    date_sown = Column(Date, nullable=False)
    container = Column(String) # 4" pot plug tray, other
    media = Column(String) # seedling media, sphagnum, other

    # covered with #2 granite grit: no, yes, lightly heavily
    covered = Column(String)

    # not same as location table, glasshouse(bottom heat, no bottom
    # heat), polyhouse, polyshade house, fridge in polybag
    location = Column(String)

    # TODO: do we need multiple moved to->moved from and date fields
    moved_from = Column(String)
    moved_to = Column(String)
    moved_date = Column(Date)

    germ_date = Column(Date)

    nseedlings = Column(Integer, autoincrement=False) # number of seedling
    germ_pct = Column(Integer, autoincrement=False) # % of germination
    date_planted = Column(Date)

    propagation_id = Column(Integer, ForeignKey('propagation.id'),
                            nullable=False)


    def __str__(self):
        # what would the string be...???
        # cuttings of self.accession.taxon_str() and accession number
        return repr(self)
