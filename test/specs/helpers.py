from faker import Faker
import pytest

import bauble.db as db
from bauble.helpers import use_model
from bauble.models import Family
import bauble.utils as utils

faker = Faker()

@pytest.fixture(scope='session', autouse=True)
def setup(app):

    @app.route('/t/<int:id>')
    @use_model(Family)
    def t_with_id(family, id):
        return utils.json_response(family.jsonify())

    @app.route('/t')
    @use_model(Family)
    def t(family):
        db.session.commit()
        return utils.json_response(family.jsonify())


def test_use_model_with_pk(client, session, family):
    session.add(family)
    session.commit()
    resp = client.get('/t/{}'.format(family.id))
    assert resp.status_code == 200
    assert resp.json['id'] == family.id


def test_use_model_without_pk(client, session):
    resp = client.get('/t')
    assert resp.status_code == 200
