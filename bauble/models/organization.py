from sqlalchemy import func, Column, DateTime, String
import sqlalchemy.dialects.postgresql as pg
import sqlalchemy.event as event
from sqlalchemy.orm import relationship, backref, object_mapper

import bauble.db as db

class Organization(db.Model):
    name = Column(String)
    short_name = Column(String)

    # pg_user and pg_schema should be the same, these are create automatically
    # when a a new account is created
    pg_user = Column(String, unique=True)
    pg_schema = Column(String, unique=True)

    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip = Column(String)

    owners = relationship('User', cascade='save-update, merge, expunge, refresh-expire',  # cascade='all, delete-orphan',
                          primaryjoin="and_("
                          "Organization.id==User.organization_id,"
                          "User.is_org_owner==True)")
    admins = relationship('User', cascade='save-update, merge, expunge, refresh-expire',  # cascade=None,
                          primaryjoin="and_("
                          "Organization.id==User.organization_id,"
                          "or_(User.is_org_owner==True, User.is_org_admin)==True)")
    users = relationship('User', cascade='save-update, merge, expunge, refresh-expire',
                         primaryjoin=("Organization.id==User.organization_id"),
                         backref=backref("organization", uselist=False), cascade_backrefs=True)

    date_approved = Column(DateTime(True))
    date_created = Column(DateTime(True), default=func.now())
    date_suspended = Column(DateTime(True))


    def __str__(self):
        return str(self.name)


    def json(self, pick=None):
        d = super().json(pick)
        d['owners'] = [owner.id for owner in self.owners]
        d['users'] = [user.id for user in self.users]
        del d['pg_schema']
        del d['pg_user']
        return d



@event.listens_for(Organization, 'before_insert')
def before_insert(mapper, connection, organization):
    # new organiations require at least one owner
    if(len(organization.owners) < 1):
        raise ValueError("An owner user is required for new organizations")


@event.listens_for(Organization, 'after_insert')
def after_insert(mapper, connection, organization):
    """
    Create a unique PostgreSQL schema for organization and set it's name on the
    organizations pg_schema field.
    """
    org_table = object_mapper(organization).local_table
    schema_name = db.create_unique_schema()
    stmt = org_table.update().where(org_table.c.id==organization.id)\
        .values(pg_schema=schema_name)
    connection.execute(stmt)


@event.listens_for(Organization, 'after_delete')
def after_delete(mapper, connection, organization):
    """
    Drop the organization's database schema when the organization is deleted.
    """
    connection.execute("drop schema {} cascade;".format(organization.pg_schema))
