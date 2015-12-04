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
    assert 'str' in accession_json
    assert accession_json['taxon']['id'] == accession.taxon_id


def test_index_accession(client, session, accession):
    session.add(accession)
    session.commit()
    resp = client.get('/api/accession')
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == accession.id


def test_post_accession(client, session, taxon):
    session.add(taxon)
    session.commit()
    code = faker.pystr(10)
    data = {'code': code, 'taxon_id': taxon.id}
    resp = client.post('/api/accession', data=data)
    assert resp.status_code == 201
    assert resp.json['id'] is not None
    assert resp.json['code'] == code


def test_patch_accession(client, session, accession):
    session.add(accession)
    session.commit()
    accession.code = faker.pystr(10)
    data = json.dumps(accession.jsonify())
    resp = client.patch('/api/accession/{}'.format(accession.id), data=data)
    assert resp.status_code == 200
    assert resp.json['id'] == accession.id
    assert resp.json['code'] == accession.code


def test_count(client, session, accession, plant):
    session.add_all([accession, plant])
    session.commit()
    resp = client.get('/api/accession/{}/count'.format(accession.id), query_string={
        'relation': ['/plants']
    })
    assert resp.status_code == 200, resp.data
    data = resp.json
    assert data['plants'] == 1
