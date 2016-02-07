from faker import Faker
from flask import json

from bauble.models import Location

faker = Faker()

def test_serializer(session, location):
    session.add(location)
    session.commit()
    location_json = location.jsonify()
    # class and instance json are the same
    assert Location.jsonify(location) == location_json
    assert 'str' in location_json


def test_index_location(client, session, location):
    session.add(location)
    session.commit()
    resp = client.get('/location')
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == location.id


def test_post_location(client, session):
    code = faker.pystr(6)
    data = {'code': code}
    resp = client.post('/location', data=data)
    assert resp.status_code == 201
    assert resp.json['id'] is not None
    assert resp.json['code'] == code


def test_patch_location(client, session, location):
    session.add(location)
    session.commit()
    location.code = faker.pystr(6)
    data = json.dumps(location.jsonify())
    resp = client.patch('/location/{}'.format(location.id), data=data)
    assert resp.status_code == 200
    assert resp.json['id'] == location.id
    assert resp.json['code'] == location.code


def test_count(client, session, location):
    pass
