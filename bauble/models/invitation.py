from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, backref

import bauble.db as db


class Invitation(db.Model):

    email = Column(String, nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    token_expiration = Column(DateTime(True))
    date_sent = Column(DateTime(True), nullable=False)
    message = Column(String)
    accepted = Column(Boolean, default=False)

    invited_by_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    invited_by = relationship('User', uselist=False,
                              backref=backref('invitations',
                                              cascade="all, delete-orphan"))

    organization_id = Column(Integer, ForeignKey('organization.id'), nullable=False)
    organization = relationship('Organization', uselist=False,
                                backref=backref('invitations',
                                                cascade="all, delete-orphan",))
