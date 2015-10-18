import os

from flask import (abort, current_app, flash, redirect, render_template,
                   request, session, url_for, Blueprint)
from flask.ext.login import logout_user, login_required, login_user, UserMixin

from bauble.models import User

root_path, _ = os.path.split(__file__)

blueprint = bp = Blueprint('auth', __name__)

# class AuthedUser(UserMixin):

#     def __init__(self, email, groups):
#         self.email = email
#         # self.picture = picture
#         self.groups = groups

#     @staticmethod
#     def from_google_userinfo(userinfo):
#         u = AuthedUser(userinfo['email'], [])
#         return u

#     def is_authenticated(self):
#         return self.email.endswith('nextglass.co')

#     def is_active(self):
#         return self.email.endswith('nextglass.co')

#     def get_id(self):
#         return self.email


def load_user(user_id):
    return User.query.get(user_id)


@bp.route('/login')
def login():
    return render_template('login.html')


# @bp.route('/unauthorized')
# def unauthorized():
#     return render_template('auth/unauthorized.html')


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@bp.route('/signup')
def signup():
    return render_template('signup.html')
