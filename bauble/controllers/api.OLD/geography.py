from flask.ext.login import login_required

from bauble.controllers.api import api
from bauble.models import Geography
import bauble.utils as utils


@api.route("/geographies")
@login_required
def list_geography():
    geographies = Geography.query.all()
    return utils.json_response(Geography.jsonify(geographies, many=True))


@api.route("/geographies/<int:geography_id>")
@login_required
def get_geography(geography_id):
    geography = Geography.query.get_or_404(geography_id)
    return utils.json_response(geography.jsonify())
