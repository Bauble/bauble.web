import os

from flask import redirect, url_for, Blueprint
from flask.ext.login import login_required

root_path, _ = os.path.split(__file__)

blueprint = bp = Blueprint('index', __name__)


@bp.route('/')
@login_required
def index(path):
    return redirect(url_for('search.index'))
