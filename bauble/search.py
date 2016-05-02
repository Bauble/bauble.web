from flask.ext.babel import gettext as _, ngettext as _n
from pyparsing import *
from sqlalchemy import *
from sqlalchemy.orm import *

import bauble
import bauble.i18n
from bauble.error import check, BaubleError

#from bauble.utils.log import debug
import bauble.utils as utils

# TODO: remove date columns from searches

# TODO: show list of completions of valid values, maybe even create
# combos for enum types values instead of text entries

def search(text, session):
    results = dict()
    for strategy in _search_strategies:
        results.update(strategy.search(text, session))
    return results



class SearchParser(object):
    """
    The parser for bauble.search.MapperSearch
    """
    value_chars = Word(alphanums + '%.-_*;:')
    # value can contain any string once its quoted
    value = value_chars | quotedString.setParseAction(removeQuotes)
    value_list = (value ^ delimitedList(value) ^ OneOrMore(value))
    binop = oneOf('= == != <> < <= > >= not like contains has ilike '
                  'icontains ihas is')('binop')
    domain = Word(alphas, alphanums)('domain')
    domain_values = Group(value_list.copy())
    domain_expression = (domain + Literal('=') + Literal('*') + StringEnd()) \
        | (domain + binop + domain_values + StringEnd())

    and_token = CaselessKeyword('and')
    or_token = CaselessKeyword('or')
    log_op = and_token | or_token

    identifier = Group(delimitedList(Word(alphas, alphanums + '_'), '.'))
    ident_expression = Group(identifier + binop + value)
    query_expression = ident_expression + ZeroOrMore(log_op + ident_expression)
    query = domain + CaselessKeyword('where').suppress() + Group(query_expression) + StringEnd()

    statement = query | domain_expression | value_list


    def parse_string(self, text):
        '''
        returns a pyparsing.ParseResults objects that represents either a
        query, an expression or a list of values
        '''
        return self.statement.parseString(text)



class SearchStrategy(object):
    """
    Interface for adding search strategies to a view.
    """

    def search(self, text, session):
        '''
        :param text: the search string
        :param session: the session to use for the search

        Return an iterator that iterates over mapped classes retrieved
        from the search.
        '''
        pass



class MapperSearch(SearchStrategy):

    """
    Mapper Search support three types of search expression:
    1. value searches: search that are just list of values, e.g. value1,
    value2, value3, searches all domains and registered columns for values
    2. expression searches: searched of the form domain=value, resolves the
    domain and searches specific columns from the mapping
    3. query searchs: searches of the form domain where ident.ident = value,
    resolve the domain and identifiers and search for value
    """

    _domains = {}
    _shorthand = {}

    # a map of classes to the class properties to search
    _properties = {}

    # a map of the class to the result key, this will be domain[0] from add_meta
    _result_keys = {}

    def __init__(self):
        super(MapperSearch, self).__init__()
        self._results = {}
        self.parser = SearchParser()


    def add_meta(self, domain, cls, properties):
        """
        Adds search meta to the domain

        :param domain: a string, list or tuple of domains that will resolve
        to cls a search string, domain act as a shorthand to the class name
        :param cls: the class the domain will resolve to
        :param properties: a list of string names of the properties to
        search by default
        """
        check(isinstance(properties, list), _('MapperSearch.add_meta(): '
                                              'default_columns argument must be list'))
        check(len(properties) > 0, _('MapperSearch.add_meta(): '
                                     'default_columns argument cannot be empty'))
        if isinstance(domain, (list, tuple)):
            # domain[0] is the result key
            self._result_keys[cls] = domain[0]
            self._domains[domain[0]] = cls, properties
            for d in domain[1:]:
                self._shorthand[d] = domain[0]
        else:
            self._result_keys[cls] = domain
            self._domains[d] = cls, properties
        self._properties[cls] = properties


    @classmethod
    def get_domain_classes(cls):
        d = {}
        for domain, item in cls._domains.items():
            d.setdefault(domain, item[0])
        return d


    def on_query(self, s, loc, tokens):
        """
        Called when the parser hits a query token.

        Queries can use more database specific features.  This also
        means that the same query might not work the same on different
        database types. For example, on a PostgreSQL database you can
        use ilike but this would raise an error on SQLite.
        """
        # The method requires that the underlying database support
        # union and intersect. At the time of writing this MySQL
        # didn't.

        # TODO: support 'not' a boolean op as well, e.g sp where
        # genus.genus=Maxillaria and not genus.family=Orchidaceae
        domain, expr = tokens
        check(domain in self._domains or domain in self._shorthand,
              'Unknown search domain: %s' % domain)
        if domain in self._shorthand:
            domain = self._shorthand[domain]
        cls = self._domains[domain][0]
        main_query = self._session.query(cls)
        mapper = class_mapper(cls)
        expr_iter = iter(expr)
        boolop = None
        for e in expr_iter:
            idents, cond, val = e
            # debug('cls: %s, idents: %s, cond: %s, val: %s'
            #       % (cls.__name__, idents, cond, val))
            if val == 'None':
                val = None
            if cond == 'is':
                cond = '='
            elif cond == 'is not':
                cond = '!='
            elif cond in ('ilike', 'icontains', 'ihas'):
                return col.op.ilike(val)
                # cond = lambda col: \
                #     lambda val: utils.ilike(col, '%s' % val)


            if len(idents) == 1:
                # we get here when the idents only refer to a property
                # on the mapper table..i.e. a column
                col = idents[0]
                msg = _('The %(tablename)s table does not have a '\
                        'column named "%(columname)s"') % \
                       dict(tablename=mapper.local_table.name,
                            columname=col)
                check(col in mapper.c, msg)
                if isinstance(cond, str):
                    #clause = getattr(cls, col).op(cond)(utils.utf8(val))
                    clause = getattr(cls, col).op(cond)(val)
                else:
                    #clause = cond(getattr(cls, col))(utils.utf8(val))
                    clause = cond(getattr(cls, col))(val)
                query = self._session.query(cls).filter(clause).order_by(None)
            else:
                # we get here when the idents refer to a relation on a
                # mapper/table
                relations = idents[:-1]
                col = idents[-1]
                query = self._session.query(cls)
                query = query.join(*relations)

                # NOTE: SA07 - this depends on Query._joinpoint not changing,
                # it changed in SA05 which broke this
                local_table = query._joinpoint['prev'][0][1].local_table
                if isinstance(cond, str):
                    #clause = local_table.c[col].op(cond)(utils.utf8(val))
                    clause = local_table.c[col].op(cond)(val)
                else:
                    #clause = cond(local_table.c[col])(utils.utf8(val))
                    clause = cond(local_table.c[col])(val)
                query = query.filter(clause).order_by(None)

            if boolop == 'or':
                main_query = main_query.union(query)
            elif boolop == 'and':
                main_query = main_query.intersect(query)
            else:
                main_query = query

            try:
                boolop = next(expr_iter)
            except StopIteration:
                pass

        self._results[self._result_keys[cls]] = main_query.order_by(None).all()


    def on_domain_expression(self, s, loc, tokens):
        """
        Called when the parser hits a domain_expression token.

        Searching using domain expressions is a little more magical
        and queries mapper properties that were passed to add_meta()

        To do a case sensitive search for a specific string use the
        double equals, '=='
        """
        domain, cond, values = tokens
        try:
            if domain in self._shorthand:
                domain = self._shorthand[domain]
            cls, properties = self._domains[domain]
        except KeyError:
            raise KeyError(_('Unknown search domain: %s' % domain))

        result_key = self._result_keys[cls]
        query = self._session.query(cls)

        # select all objects from the domain
        if values == '*':
            self._results[result_key] = query.all()
            return

        mapper = class_mapper(cls)

        if cond in ('like', 'ilike', 'contains', 'icontains', 'has', 'ihas'):
            condition = lambda col: \
                lambda val: utils.ilike(mapper.c[col], '%%%s%%' % val)
        elif cond == '=':
            condition = lambda col: \
                lambda val: utils.ilike(mapper.c[col], val)
                #lambda val: utils.ilike(mapper.c[col], utils.utf8(val))
        else:
            condition = lambda col: \
                lambda val: mapper.c[col].op(cond)(val)

        ors = or_(*[condition(prop)(value) for value in values for prop in properties])
        self._results[result_key] = query.filter(ors).all()



    def on_value_list(self, s, loc, tokens):
        """
        Called when the parser hits a value_list token

        Search with a list of values is the broadest search and
        searches all the mapper and the properties configured with
        add_meta()
        """
        # print('values: %s' % tokens)
        # print('  s: %s' % s)
        # print('  loc: %s' % loc)
        # print('  toks: %s' % tokens)

        # make searches case-insensitive, in postgres use ilike,
        # in other use upper()
        # like = lambda table, col, val: \
        #     utils.ilike(table.c[col], ('%%%s%%' % val))
        like = lambda table, col, val: \
            table.c[col].ilike('%{}%'.format(val))

        for cls, columns in self._properties.items():
            q = self._session.query(cls)
            cv = [(c, v) for c in columns for v in tokens]
            mapper = class_mapper(cls)
            q = q.filter(or_(*(like(mapper, c, v) for c, v in cv)))
            self._results[self._result_keys[cls]] = q.all()



    def search(self, text, session):
        """
        Returns a set() of database hits for the text search string.

        If session=None then the session should be closed after the results
        have been processed or it is possible that some database backends
        could cause deadlocks.
        """
        self._session = session

        # this looks kinda ridiculous to add the parse actions and
        # then remove them but then it allows us to reuse the parser
        # for other things, particulary tests, without calling the
        # parse actions
        self.parser.query.setParseAction(self.on_query)
        self.parser.domain_expression.setParseAction(self.on_domain_expression)
        self.parser.value_list.setParseAction(self.on_value_list)

        self._results.clear()
        self.parser.parse_string(text)

        self.parser.query.parseAction = []
        self.parser.domain_expression.parseAction = []
        self.parser.value_list.parseAction = []

        # these results get filled in when the parse actions are called
        return self._results


"""
the search strategy is keyed by domain and each value will be a list of
SearchStrategy instances
    """
_search_strategies = [MapperSearch()]

def add_strategy(strategy):
    _search_strategies.append(strategy())


def get_strategy(name):
    for strategy in _search_strategies:
        if strategy.__class__.__name__ == name:
            return strategy
