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


def test_deserialize(session, taxon):
    from bauble.schema import schema_factory
    session.add(taxon)
    session.commit()
    taxon_json = taxon.jsonify()
    taxon, errors = schema_factory(Taxon).load(taxon_json)
    assert errors is not None and len(errors) == 0
    assert taxon_json['genus_id'] == taxon.genus_id
    assert taxon_json['sp'] == taxon.sp


def test_form(session, taxon):
    from bauble.forms import MarshmallowForm, form_factory
    session.add(taxon)
    session.commit()
    form = form_factory(taxon)
    assert form is not None


def test_index_taxon(client, session, taxon):
    session.add(taxon)
    session.commit()
    resp = client.get('/api/taxon')
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == taxon.id


def test_post_taxon_accept_json(client, session, genus):
    session.add(genus)
    session.commit()
    sp = faker.first_name()
    data = {'sp': sp, 'genus_id': genus.id}
    resp = client.post('/taxon.json', data=data)
    assert resp.status_code == 201
    assert resp.json['id'] is not None
    assert resp.json['sp'] == sp


def test_post_taxon_accept_html(client, session, genus):
    session.add(genus)
    session.commit()
    sp = faker.first_name()
    data = {'sp': sp, 'genus_id': genus.id}
    headers = {'accept': 'text/html'}
    resp = client.post('/taxon', data=data, headers=headers)
    assert resp.status_code == 201


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
