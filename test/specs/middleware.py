from faker import Faker
import pytest

from bauble.middleware import use_model
from bauble.models import Family
import bauble.utils as utils


faker = Faker()

# TODO: should POST with pk in data update or ignore the pk and create a new resource

@pytest.fixture(scope='module', autouse=True)
def test_route(app):
    @app.route('/t/<int:id>')
    @use_model(Family)
    def get(family, id):
        return utils.json_response(family.jsonify())


    @app.route('/t/<int:id>', methods=['PATCH'])
    @use_model(Family)
    def patch(family, id):
        return utils.json_response(family.jsonify())


def test_use_model_get(app, client, session, family):
    session.add(family)
    session.commit()

    resp = client.get('/t/{}'.format(family.id))
    assert resp.status_code == 200
    assert resp.json['id'] == family.id


# def test_use_model_get_index(client, session, family):
#     session.add(family)
#     session.commit()
#     resp = client.get(base_route)
#     assert resp.status_code == 200
#     assert resp.json[0]['id'] == family.id


def test_use_model_patch_with_pk_in_model(app, client, session, family):
    """
    The use_model middleware should ignore the pk in the request data.
    """
    # save fixture
    session.add(family)
    session.commit()
    data = family.jsonify()

    # modify data
    data['family'] = faker.first_name() + 'aceae'
    session.expunge(family)

    resp = client.patch('/t/{}'.format(family.id), data=data,
                        headers={'accept': 'application/json'})
    assert resp.status_code == 200
    assert resp.json['id'] == family.id
    assert resp.json['family'] == data['family']


def test_use_model_patch_without_pk_in_model(app, client, session, family):
    """
    The use_model middleware should work when the pk is not in the request data.
    """
    # save fixture
    session.add(family)
    session.commit()
    data = family.jsonify()
    session.expunge(family)

    # modify data
    data['family'] = faker.first_name() + 'aceae'
    del data['id']

    resp = client.patch('/t/{}'.format(family.id), data=data,
                        headers={'accept': 'application/json'})
    assert resp.status_code == 200
    assert resp.json['id'] == family.id
    assert resp.json['family'] == data['family']
