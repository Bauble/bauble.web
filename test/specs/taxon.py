from faker import Faker
from flask import json

from bauble.models import Taxon

faker = Faker()

def test_serializer(session, taxon):
    session.add(taxon)
    session.commit()
    taxon_json = taxon.jsonify()
    assert Taxon.jsonify(taxon) == taxon_json  # class and instance json are the same
    assert 'str' in taxon_json
    assert taxon_json['genus']['id'] == taxon.genus_id


def test_index_taxon(client, session, taxon):
    session.add(taxon)
    session.commit()
    resp = client.get('/api/taxon')
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == taxon.id


def test_post_taxon(client, session, genus):
    session.add(genus)
    session.commit()
    sp = faker.first_name()
    data = {'sp': sp, 'genus_id': genus.id}
    resp = client.post('/api/taxon', data=data)
    assert resp.status_code == 201
    print('resp.json: ', resp.json)
    assert resp.json['id'] is not None
    assert resp.json['sp'] == sp


def test_patch_taxon(client, session, taxon):
    session.add(taxon)
    session.commit()
    taxon.sp = faker.first_name()
    data = json.dumps(taxon.jsonify())
    resp = client.patch('/api/taxon/{}'.format(taxon.id), data=data)
    assert resp.status_code == 200
    assert resp.json['id'] == taxon.id
    assert resp.json['sp'] == taxon.sp


def test_count(client, session, taxon, accession, plant):
    session.add_all([taxon, accession, plant])
    session.commit()
    resp = client.get('/api/taxon/{}/count'.format(taxon.id), query_string={
        'relation': ['/accessions', '/accessions/plants']
    })
    assert resp.status_code == 200, resp.data
    data = resp.json
    assert data['accessions'] == 1
