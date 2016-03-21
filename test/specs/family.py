import json

from faker import Faker

from bauble.models import Family

faker = Faker()

def test_serializer(session, family):
    session.add(family)
    session.commit()
    family_json = family.jsonify()
    assert Family.jsonify(family) == family_json
    assert 'str' in family_json


def test_form(session, family):
    from bauble.forms import form_factory, BaseModelForm
    session.add(family)
    session.commit()
    form = form_factory(family)
    assert isinstance(form, BaseModelForm)


def test_index_family_json(client, session, family):
    session.add(family)
    session.commit()
    resp = client.get('/family')
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == family.id


def test_post_family(client, session, family):
    resp = client.post('/family', data=family.jsonify())
    assert resp.status_code == 201
    # TODO: assert response


def test_post_family_json(client, session, family):
    resp = client.post('/family.json', data=json.dumps(family.jsonify()),
                       content_type='application/json')
    assert resp.status_code == 201
    assert resp.json['id'] is not None, resp.json
    assert resp.json['family'] == family.family


def test_patch_family(client, session, family):
    session.add(family)
    session.commit()
    family.family = faker.first_name() + 'aceae'
    resp = client.patch('/family/{}'.format(family.id), data=family.jsonify())
    assert resp.status_code == 200
    # TODO: assert response


def test_patch_family_json(client, session, family):
    session.add(family)
    session.commit()
    family.family = faker.first_name() + 'aceae'
    resp = client.patch('/family/{}.json'.format(family.id), data=family.jsonify())
    assert resp.status_code == 200
    assert resp.json['id'] == family.id
    assert resp.json['family'] == family.family


def test_count(client, session, family, genus, taxon, accession):
    session.add_all([family, genus, taxon, accession])
    session.commit()
    resp = client.get('/family/{}/count'.format(family.id), query_string={
        'relation': ['/genera', '/genera/taxa', '/genera/taxa/accessions',
                     '/genera/taxa/accessions/plants']
    })
    assert resp.status_code == 200, resp.data
    data = resp.json
    assert data['genera'] == 1
