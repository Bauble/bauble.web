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
    from bauble.forms import form_factory, BaseModelForm
    session.add(genus)
    session.commit()
    form = form_factory(genus)
    assert isinstance(form, BaseModelForm)


def test_index_genus(client, session, genus):
    session.add(genus)
    session.commit()
    resp = client.get('/genus')
    assert resp.status_code == 200
    # TODO: assert response


def test_index_genus_json(client, session, genus):
    session.add(genus)
    session.commit()
    resp = client.get('/genus.json')
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == genus.id


def test_post_genus(client, session, family):
    session.add(family)
    session.commit()
    genus = faker.first_name()
    data = {'genus': genus, 'family_id': family.id}
    resp = client.post('/genus', data=data)
    assert resp.status_code == 201
    assert resp.mimetype == 'text/html'
    # TODO: assert response


def test_post_genus_json(client, session, family):
    session.add(family)
    session.commit()
    genus = faker.first_name()
    data = {'genus': genus, 'family_id': family.id}
    resp = client.post('/genus.json', data=json.dumps(data),
                       content_type='application/json')
    assert resp.status_code == 201, resp.data.decode('utf-8')
    assert resp.json['id'] is not None
    assert resp.json['genus'] == genus


def test_patch_genus(client, session, genus):
    session.add(genus)
    session.commit()
    genus.genus = faker.first_name()
    data = json.dumps(genus.jsonify())
    resp = client.patch('/genus/{}'.format(genus.id), data=data,
                        follow_redirects=True)
    assert resp.status_code == 200
    assert resp.mimetype == 'text/html'
    # TODO: test html response is what we expect


# TODO: test both PATCH and POST
def test_patch_genus_json(client, session, genus):
    session.add(genus)
    session.commit()
    genus.genus = faker.first_name()
    data = json.dumps(genus.jsonify())
    resp = client.patch('/genus/{}'.format(genus.id), data=data,
                        content_type='application/json',
                        headers={'accept': 'application/json'})
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'
    assert resp.json['id'] == genus.id
    assert resp.json['genus'] == genus.genus


def test_count(client, session, genus, taxon, accession):
    session.add_all([genus, taxon, accession])
    session.commit()
    resp = client.get('/genus/{}/count'.format(genus.id), query_string={
        'relation': ['/taxa', '/taxa/accessions', '/taxa/accessions/plants']
    })
    assert resp.status_code == 200
    data = resp.json
    assert data['taxa'] == 1
