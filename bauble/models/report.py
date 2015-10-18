from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSON

import bauble.db as db


class Report(db.Model):
    """
    :Table name: report

    :Columns:
        *name*:
            The name if of the report definition.

        *query*:
            The query string.

        *visible_columns*:
            Visible columns.

        *column_widths
            Column widths.

        *column_headers
            Column_headers


    """

    # columns
    name = Column(String, unique=True, nullable=False, index=True)
    query = Column(String)

    # JSON representation of how this report should be formated
    # properties:
    # - visible_columns: a string that represents a JSON list/array
    # - column_widths: a json object that maps column names to widths
    # - column_headers: a json object that maps column names to headers
    # - xsl_stylesheet
    # - xsl_stylesheet_filename
    setting = Column(JSON)


    # TODO: fix the created and lastupdate user relationships..for some reason there's
    # an error when calling /admin/initdb that has to do with User not being defined,
    # this is probably some weird issues with the two mappers having different metadata
    # or pg schema
    # created_by_user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    # created_by_user = relationship('User', cascade='all,delete-orphan',
    #                                primaryjoin='ReportDef.created_by_user_id==User.id')

    #last_updated_by_user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    # last_updated_by_user = relationship('User', cascade='all,delete-orphan',
    #                                     primaryjoin='ReportDef.last_updated_by_user_id==User.id')


    # TODO: do we need to customize this or can we just return the default json object
    # def json(self, pick=None):
    #     return dict(name=self.name,
    #                 query=self.query,
    #                 settings=self.settings)
    def __str__(self):
        return self.name


    def json(self):
        data = super(Report, self).json()  # py2
        data.pop('str')
        return data
