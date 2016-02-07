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


def test_deserialize(session, plant):
    from bauble.schema import schema_factory
    session.add(plant)
    session.commit()
    plant_json = plant.jsonify()
    plant, errors = schema_factory(Plant).load(plant_json)
    assert errors is not None and len(errors) == 0
    assert plant_json['accession_id'] == plant.accession_id
    assert plant_json['code'] == plant.code


def test_form(session, plant):
    from bauble.forms import MarshmallowForm, form_factory
    session.add(plant)
    session.commit()
    form = form_factory(plant)
    assert form is not None


def test_index_plant(client, session, plant):
    session.add(plant)
    session.commit()
    resp = client.get('/plant')
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == plant.id


def test_post_plant(client, session, accession, location):
    session.add_all([accession, location])
    session.commit()
    code = faker.pystr(6)
    data = {'code': code, 'quantity': faker.pyint(), 'accession_id': accession.id,
            'location_id': location.id}
    resp = client.post('/plant', data=data)
    assert resp.status_code == 201
    assert resp.mimetype == 'text/html'
    # TODO: check that errors were added to rendered html or in the flash messages


def test_post_plant_json(client, session, accession, location):
    session.add_all([accession, location])
    session.commit()
    code = faker.pystr(6)
    data = {'code': code, 'quantity': faker.pyint(), 'accession_id': accession.id,
            'location_id': location.id}
    resp = client.post('/plant', data=json.dumps(data),
                       content_type='application/json',
                       headers={'accept': 'application/json'})
    assert resp.status_code == 201
    assert resp.json['id'] is not None
    assert resp.json['code'] == code


def test_patch_plant(client, session, plant):
    session.add(plant)
    session.commit()
    plant.code = faker.pystr(6)
    data = json.dumps(plant.jsonify())
    resp = client.patch('/plant/{}'.format(plant.id), data=data)
    # assert resp.status_code == 200
    assert resp.mimetype == 'text/html'


def test_patch_plant_json(client, session, plant):
    session.add(plant)
    session.commit()
    plant.code = faker.pystr(6)
    data = json.dumps(plant.jsonify())
    resp = client.patch('/plant/{}'.format(plant.id), data=data,
                        content_type='application/json',
                        headers={'accept': 'application/json'})
    assert resp.status_code == 200
    assert resp.json['id'] == plant.id
    assert resp.json['code'] == plant.code


def test_count(client, session, plant):
    pass
