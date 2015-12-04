from faker import Faker
from flask import json

from bauble.models import Plant

faker = Faker()

def test_serializer(session, plant):
    session.add(plant)
    session.commit()
    plant_json = plant.jsonify()
    # class and instance json are the same
    assert Plant.jsonify(plant) == plant_json
    assert 'str' in plant_json
    assert plant_json['accession']['id'] == plant.accession_id


def test_index_plant(client, session, plant):
    session.add(plant)
    session.commit()
    resp = client.get('/api/plant')
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == plant.id


def test_post_plant(client, session, accession, location):
    session.add_all([accession, location])
    session.commit()
    code = faker.pystr(6)
    data = {'code': code, 'quantity': faker.pyint(), 'accession_id': accession.id,
            'location_id': location.id}
    resp = client.post('/api/plant', data=data)
    assert resp.status_code == 201
    assert resp.json['id'] is not None
    assert resp.json['code'] == code


def test_patch_plant(client, session, plant):
    session.add(plant)
    session.commit()
    plant.code = faker.pystr(6)
    data = json.dumps(plant.jsonify())
    resp = client.patch('/api/plant/{}'.format(plant.id), data=data)
    assert resp.status_code == 200
    assert resp.json['id'] == plant.id
    assert resp.json['code'] == plant.code


def test_count(client, session, plant):
    pass
