from faker import Faker
from flask import json

from bauble.models import VernacularName

faker = Faker()

def test_serializer(session, vernacular_name):
    session.add(vernacular_name)
    session.commit()
    vernacular_name_json = vernacular_name.jsonify()
    assert VernacularName.jsonify(vernacular_name) == vernacular_name_json  # class and instance json are the same
    assert 'str' in vernacular_name_json
    assert vernacular_name_json['taxon']['id'] == vernacular_name.taxon_id


def test_deserialize(session, vernacular_name):
    from bauble.schema import schema_factory
    session.add(vernacular_name)
    session.commit()
    vernacular_name_json = vernacular_name.jsonify()
    vernacular_name, errors = schema_factory(VernacularName).load(vernacular_name_json)
    assert errors is not None and len(errors) == 0
    assert vernacular_name_json['taxon_id'] == vernacular_name.taxon_id
    assert vernacular_name_json['name'] == vernacular_name.name


def test_form(session, vernacular_name):
    from bauble.forms import form_factory, BaseModelForm
    session.add(vernacular_name)
    session.commit()
    form = form_factory(vernacular_name)
    assert isinstance(form, BaseModelForm)


def test_index_vernacular_name_json(client, session, vernacular_name):
    session.add(vernacular_name)
    session.commit()
    resp = client.get('/taxon/{}/vernacular_name'.format(vernacular_name.taxon.id))
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == vernacular_name.id


def test_post_vernacular_name_json(client, session, taxon):
    session.add(taxon)
    session.commit()
    name = faker.first_name()
    # TODO: taxon_id shouldn't be required or should probably be ignored
    # since we posting to a taxon relative url
    data = {'name': name, 'taxon_id': taxon.id}
    resp = client.post('/taxon/{}/vernacular_name.json'.format(taxon.id), data=data)
    assert resp.status_code == 201, resp.data.decode('utf-8')
    assert resp.json['id'] is not None
    assert resp.json['name'] == name


def test_post_vernacular_name(client, session, taxon):
    session.add(taxon)
    session.commit()
    sp = faker.first_name()
    data = {'sp': sp, 'taxon_id': taxon.id}
    resp = client.post('/taxon/{}/vernacular_name'.format(taxon.id), data=data)
    assert resp.status_code == 201
    assert resp.mimetype == 'text/html'


# def test_post_vernacular_name_json(client, session, taxon):
#     session.add(taxon)
#     session.commit()
#     sp = faker.first_name()
#     data = {'sp': sp, 'taxon_id': taxon.id}
#     resp = client.post('/taxon/{}/vernacular_name.json'.format(taxon.id), data=json.dumps(data),
#                        content_type='application/json')
#     assert resp.mimetype == 'application/json'
#     assert resp.status_code == 201


# TODO: test both PATCH and POST
def test_patch_vernacular_name(client, session, vernacular_name):
    session.add(vernacular_name)
    session.commit()
    vernacular_name.sp = faker.first_name()
    data = json.dumps(vernacular_name.jsonify())
    resp = client.patch('/taxon/{}/vernacular_name/{}'.format(vernacular_name.taxon.id, vernacular_name.id), data=data,
                        follow_redirects=True)
    assert resp.status_code == 204
    assert resp.mimetype == 'text/html'


# TODO: test both PATCH and POST
def test_patch_vernacular_name_json(client, session, vernacular_name):
    session.add(vernacular_name)
    session.commit()
    vernacular_name.name = faker.first_name()
    data = json.dumps(vernacular_name.jsonify())
    resp = client.patch('/taxon/{}/vernacular_name/{}.json'.format(vernacular_name.taxon.id,
                                                                   vernacular_name.id), data=data,
                        content_type='application/json')
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'
    assert resp.json['id'] == vernacular_name.id
    assert resp.json['name'] == vernacular_name.name


def test_delete_vernacular_name(client, session, vernacular_name):
    session.add(vernacular_name)
    session.commit()
    url = '/taxon/{}/vernacular_name/{}'.format(vernacular_name.taxon.id, vernacular_name.id)
    resp = client.delete('/taxon/{}/vernacular_name/{}'.format(vernacular_name.taxon.id,
                                                               vernacular_name.id))
    assert resp.status_code == 204
