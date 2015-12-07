from faker import Faker

faker = Faker()

base_route = '/api/family'

# TODO: should POST with pk in data update or ignore the pk and create a new resource

def test_use_model_get(client, session, family):
    session.add(family)
    session.commit()
    resp = client.get('{}/{}'.format(base_route, family.id))
    assert resp.status_code == 200
    assert resp.json['id'] == family.id


def test_use_model_get_index(client, session, family):
    session.add(family)
    session.commit()
    resp = client.get(base_route)
    assert resp.status_code == 200
    assert resp.json[0]['id'] == family.id


def test_use_model_patch_with_pk_in_model(client, session, family):
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

    resp = client.patch('{}/{}'.format(base_route, family.id), data=data)
    assert resp.status_code == 200
    assert resp.json['id'] == family.id
    assert resp.json['family'] == data['family']


def test_use_model_patch_without_pk_in_model(client, session, family):
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

    resp = client.patch('{}/{}'.format(base_route, family.id), data=data)
    assert resp.status_code == 200
    assert resp.json['id'] == family.id
    assert resp.json['family'] == data['family']
