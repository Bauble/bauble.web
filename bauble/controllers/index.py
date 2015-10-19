import os

from flask import (abort, current_app, flash, redirect, render_template,
                   request, session, url_for, Blueprint)
from flask.ext.login import login_required

from bauble.models import User

root_path, _ = os.path.split(__file__)

blueprint = bp = Blueprint('index', __name__)


# @bp.route('/', defaults={'path': ''})
@bp.route('/<path:path>')
@login_required
def index(path):
    return render_template('index.html')
