from faker import Faker
from flask import json

from bauble.models import Genus

faker = Faker()

def test_serializer(session, genus):
    session.add(genus)
    session.commit()
    genus_json = genus.jsonify()
    assert Genus.jsonify(genus) == genus_json  # class and instance json are the same
    assert 'str' in genus_json
    assert genus_json['family']['id'] == genus.family_id


def test_form(session, genus):
    from bauble.forms import MarshmallowForm, form_factory
    session.add(genus)
    session.commit()
    form = form_factory(genus)
    assert form is not None


def test_index_genus(client, session, genus):
    session.add(genus)
    session.commit()
    resp = client.get('/api/genus')
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == genus.id


def test_post_genus(client, session, family):
    session.add(family)
    session.commit()
    genus = faker.first_name()
    data = {'genus': genus, 'family_id': family.id}
    resp = client.post('/api/genus', data=data)
    assert resp.status_code == 201
    assert resp.json['id'] is not None
    assert resp.json['genus'] == genus


def test_patch_genus(client, session, genus):
    session.add(genus)
    session.commit()
    genus.genus = faker.first_name()
    data = json.dumps(genus.jsonify())
    resp = client.patch('/api/genus/{}'.format(genus.id), data=data)
    assert resp.status_code == 200
    assert resp.json['id'] == genus.id
    assert resp.json['genus'] == genus.genus


def test_count(client, session, genus, taxon, accession):
    session.add_all([genus, taxon, accession])
    session.commit()
    resp = client.get('/api/genus/{}/count'.format(genus.id), query_string={
        'relation': ['/taxa', '/taxa/accessions', '/taxa/accessions/plants']
    })
    assert resp.status_code == 200, resp.data
    data = resp.json
    assert data['taxa'] == 1
