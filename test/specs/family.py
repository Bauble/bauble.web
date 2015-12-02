from faker import Faker

from bauble.models import Family

faker = Faker()

def test_serializer(session, family):
    session.add(family)
    session.commit()
    family_json = family.jsonify()
    assert Family.jsonify(family) == family_json
    assert 'str' in family_json


def test_index_family(client, session, family):
    session.add(family)
    session.commit()
    resp = client.get('/api/family')
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == family.id


def test_post_family(client, session, family):
    resp = client.post('/api/family', data=family.jsonify())
    assert resp.status_code == 201
    assert resp.json['id'] is not None
    assert resp.json['family'] == family.family

def test_patch_family(client, session, family):
    session.add(family)
    session.commit()
    family.family = faker.first_name() + 'aceae'
    resp = client.patch('/api/family/{}'.format(family.id), data=family.jsonify())
    assert resp.status_code == 200
    assert resp.json['id'] == family.id
    assert resp.json['family'] == family.family


def test_count(client, session, family, genus, taxon, accession):
    session.add_all([family, genus, taxon, accession])
    session.commit()
    resp = client.get('/api/family/{}/count'.format(family.id), query_string={
        'relation': ['/genera', '/genera/taxa', '/genera/taxa/accessions',
                     '/genera/taxa/accessions/plants']
    })
    assert resp.status_code == 200, resp.data
    data = resp.json
    assert data['genera'] == 1
