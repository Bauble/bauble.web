import bcrypt
from flask.ext.login import UserMixin
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import Comparator, hybrid_property

import bauble.db as db


class EncryptedPassword(Comparator):
    """
    Comparator to handle encrypted passwords.
    """

    def __init__(self, password):
        self._password = password

    def operate(self, op, other):
        if not isinstance(other, EncryptedPassword):
            encode = lambda s: s.encode("utf-8") if s else "".encode("utf-8")
            other = bcrypt.hashpw(encode(other), encode(self._password)).decode('utf-8')
        return op(self._password, other)

    def __clause_element__(self):
        return self._password

    def __str__(self):
        return self._password


class User(db.Model, UserMixin):

    def __init__(self, *args, password=None, **kwargs):
        self.password = password if password else ""
        super().__init__(*args, **kwargs)

        self.username = self.email if not self.username else self.username


    username = Column(String, nullable=False, unique=True)
    fullname = Column(String)
    title = Column(String)
    email = Column(String, nullable=False, unique=True)

    timezone = Column(String)

    # All requests after /login will use the access token for authentication
    # rather than the password.  An access token as an expiration date.
    access_token = Column(String, unique=True)

    # TODO: we need to encrypt our access_token

    # The date and time when the access_token expires.
    access_token_expiration = Column(DateTime(True))

    # system permissions
    is_sysadmin = Column(Boolean)
    is_org_owner = Column(Boolean)
    is_org_admin = Column(Boolean)

    last_accessed = Column(DateTime(True))
    date_suspended = Column(Date)

    password_reset_token = Column(String)
    password_reset_token_expiration = Column(DateTime(True))

    # the user->organization relationship is created as a backref on the
    # organization object
    organization_id = Column(Integer, ForeignKey('organization.id'))

    _password = Column('password', String, nullable=False,
                       info={'dumpable': False})  # hybrid property, see below

    @hybrid_property
    def password(self):
        return EncryptedPassword(self._password)


    @password.setter
    def set_password(self, password):
        """Encrypt and set the password.
        """
        self._password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode('utf-8')


    def __str__(self):
        return self.username if self.username else self.email
