from faker import Faker
from flask import json

from bauble.models import Accession

faker = Faker()

def test_serializer(session, accession):
    session.add(accession)
    session.commit()
    accession_json = accession.jsonify()
    # class and instance json are the same
    assert Accession.jsonify(accession) == accession_json
    assert accession_json['taxon']['id'] == accession.taxon_id
    assert accession_json['taxon_str'] == accession.taxon_str()


def test_deserialize(session, accession):
    from bauble.schema import schema_factory
    session.add(accession)
    session.commit()
    accession_json = accession.jsonify()
    accession, errors = schema_factory(Accession).load(accession_json)
    assert errors is not None and len(errors) == 0
    assert accession_json['taxon_id'] == accession.taxon_id
    assert accession_json['code'] == accession.code


def test_form(session, accession):
    from bauble.forms import MarshmallowForm, form_factory
    session.add(accession)
    session.commit()
    form = form_factory(accession)
    assert form is not None


def test_index_accession(client, session, accession):
    session.add(accession)
    session.commit()
    resp = client.get('/accession')
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == accession.id


def test_post_accession(client, session, taxon):
    session.add(taxon)
    session.commit()
    code = faker.pystr(10)
    data = {'code': code, 'taxon_id': taxon.id}
    resp = client.post('/accession', data=data)
    assert resp.status_code == 201
    assert resp.mimetype == 'text/html'


def test_post_accession_with_error(client, session, taxon):
    session.add(taxon)
    session.commit()
    code = faker.pystr(10)
    # date is not formatted in ISO8601
    data = {'code': code, 'taxon_id': taxon.id, 'date_recvd': '1-1-2001'}
    resp = client.post('/accession', data=data)
    assert resp.status_code == 200
    assert resp.mimetype == 'text/html'
    # TODO: check that errors were added to rendered html or in the flash messages


def test_post_accession_json(client, session, taxon):
    session.add(taxon)
    session.commit()
    code = faker.pystr(10)
    data = {'code': code, 'taxon_id': taxon.id, 'date_recvd': '2010-1-30'}
    resp = client.post('/accession', data=json.dumps(data),
                       content_type='application/json',
                       headers={'accept': 'application/json'})
    assert resp.status_code == 201, resp.data.decode('utf-8')
    assert resp.json['id'] is not None
    assert resp.json['code'] == code

def test_post_accession_json_with_errors(client, session, taxon):
    session.add(taxon)
    session.commit()
    code = faker.pystr(10)
    data = {'code': code, 'taxon_id': taxon.id, 'date_recvd': '1-30-2010'}
    resp = client.post('/accession', data=json.dumps(data),
                       content_type='application/json',
                       headers={'accept': 'application/json'})
    assert resp.status_code == 422, resp.data.decode('utf-8')
    # TODO: check for errors



def test_patch_accession(client, session, accession):
    session.add(accession)
    session.commit()
    accession.code = faker.pystr(10)
    data = json.dumps(accession.jsonify())
    resp = client.patch('/accession/{}'.format(accession.id), data=data)
    assert resp.mimetype == 'text/html'


def test_patch_accession_json(client, session, accession):
    session.add(accession)
    session.commit()
    accession.code = faker.pystr(10)
    data = json.dumps(accession.jsonify())
    resp = client.patch('/accession/{}'.format(accession.id), data=data,
                        content_type='application/json',
                        headers={'accept': 'application/json'})
    assert resp.status_code == 200
    assert resp.json['id'] == accession.id
    assert resp.json['code'] == accession.code


def test_count(client, session, accession, plant):
    session.add_all([accession, plant])
    session.commit()
    resp = client.get('/accession/{}/count'.format(accession.id), query_string={
        'relation': ['/plants']
    })
    assert resp.status_code == 200, resp.data.decode('utf-8')
    data = resp.json
    assert data['plants'] == 1
