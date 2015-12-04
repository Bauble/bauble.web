from sqlalchemy import Column, String, Text
from sqlalchemy.orm import backref, relationship

import bauble.db as db
import bauble.search as search


def loc_markup_func(location):
    if location.description is not None:
        return utils.xml_safe(str(location)), \
            utils.xml_safe(str(location.description))
    else:
        return utils.xml_safe(str(location))


class Location(db.Model):
    """
    :Table name: location

    :Columns:
        *name*:

        *description*:

    :Relation:
        *plants*:

    """
    __mapper_args__ = {'order_by': 'name'}

    # refers to beds by unique codes
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(64))
    description = Column(Text)

    def __str__(self):
        if self.name:
            return '(%s) %s' % (self.code, self.name)
        else:
            return str(self.code)


    def json(self, depth=1):
        d = dict(ref="/location/" + str(self.id))
        if depth > 0:
            d['id'] = self.id
            d['code'] = self.code
            d['name'] = self.name
            d['str'] = str(self)
        if depth > 1:
            d['description'] = self.description

        return d


# setup the search mapper
mapper_search = search.get_strategy('MapperSearch')
mapper_search.add_meta(('locations', 'location', 'loc'), Location, ['name', 'code'])
