from faker import Faker
from flask import json

import bauble.db as db
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


def test_form(session, genus, taxon):
    # from bauble.forms import form_factory, BaseModelForm
    from bauble.controllers.taxon import TaxonForm
    session.add(taxon)
    session.commit()
    data = {
        'sp': faker.first_name(),
        'genus_id': genus.id,
        'vernacular_names': [{
            'name': faker.first_name(),
            'language': 'Macedamian',
            '_destroy': True
        }]
    }
    form = TaxonForm(data=data)
    taxon = Taxon()
    form.populate_obj(taxon)
    for key, value in form.data.items():
        print('{} - {}'.format(key, value))
    db.session.add(taxon)
    db.session.commit()
    print('taxon.vernacular_names: ', taxon.vernacular_names)
    assert len(data['vernacular_names']) == len(taxon.vernacular_names)
    for vn in taxon.vernacular_names:
        assert vn.id is not None
    db.session.refresh(taxon)
    assert taxon.id is not None
    # form = form_factory(taxon)
    # assert isinstance(form, BaseModelForm)


def test_index_taxon_json(client, session, taxon):
    session.add(taxon)
    session.commit()
    resp = client.get('/taxon')
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == taxon.id


def test_post_taxon_json(client, session, genus):
    session.add(genus)
    session.commit()
    sp = faker.first_name()
    data = {
        'sp': sp,
        'genus_id': genus.id,
        'vernacular_names': [{
            'name': faker.first_name(),
            'language': 'Macedamian'
        }]
    }
    resp = client.post('/taxon.json', data=json.dumps(data),
                       content_type='application/json')
    assert resp.status_code == 201, resp.data.decode('utf-8')
    assert resp.json['id'] is not None
    assert resp.json['sp'] == sp

    taxon = Taxon.query.get_or_404(resp.json['id'])
    assert len(data['vernacular_names']) == len(taxon.vernacular_names)


def test_post_taxon(client, session, genus):
    session.add(genus)
    session.commit()
    sp = faker.first_name()
    data = {
        'sp': sp,
        'genus_id': genus.id,
        'vernacular_names': [{
            'name': faker.first_name(),
            'language': 'Macedamian'
        }]
    }
    resp = client.post('/taxon', data=data)
    assert resp.status_code == 201
    assert resp.mimetype == 'text/html'


# def test_post_taxon_json(client, session, genus):
#     session.add(genus)
#     session.commit()
#     sp = faker.first_name()
#     data = {'sp': sp, 'genus_id': genus.id}
#     resp = client.post('/taxon.json', data=json.dumps(data),
#                        content_type='application/json')
#     assert resp.mimetype == 'application/json'
#     assert resp.status_code == 201


# TODO: test both PATCH and POST
def test_patch_taxon(client, session, taxon):
    session.add(taxon)
    session.commit()
    taxon.sp = faker.first_name()
    data = json.dumps(taxon.jsonify())
    resp = client.patch('/taxon/{}'.format(taxon.id), data=data,
                        follow_redirects=True)
    assert resp.status_code == 200
    assert resp.mimetype == 'text/html'
    # TODO: test html response is what we expect


# TODO: test both PATCH and POST
def test_patch_taxon_json(client, session, taxon):
    session.add(taxon)
    session.commit()
    taxon.sp = faker.first_name()
    data = json.dumps(taxon.jsonify())
    resp = client.patch('/taxon/{}.json'.format(taxon.id), data=data,
                        content_type='application/json')
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'
    assert resp.json['id'] == taxon.id
    assert resp.json['sp'] == taxon.sp


def test_count(client, session, taxon, accession, plant):
    session.add_all([taxon, accession, plant])
    session.commit()
    resp = client.get('/taxon/{}/count'.format(taxon.id), query_string={
        'relation': ['/accessions', '/accessions/plants']
    })
    assert resp.status_code == 200
    data = resp.json
    assert data['accessions'] == 1
