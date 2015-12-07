from faker import Faker

from bauble.models import SourceDetail

faker = Faker()

def test_serializer(session, source_detail):
    session.add(source_detail)
    session.commit()
    source_json = source_detail.jsonify()
    assert SourceDetail.jsonify(source_detail) == source_json
    assert 'str' in source_json

def test_index_source(client, session, source_detail):
    session.add(source_detail)
    session.commit()
    resp = client.get('/api/source')
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == source_detail.id

def test_post_source(client, session, source_detail):
    resp = client.post('/api/source', data=source_detail.jsonify())
    assert resp.status_code == 201
    assert resp.json['id'] is not None
    assert resp.json['name'] == source_detail.name

def test_patch_source(client, session, source_detail):
    session.add(source_detail)
    session.commit()
    source_detail.name = faker.first_name()
    resp = client.patch('/api/source/{}'.format(source_detail.id),
                        data=source_detail.jsonify())
    assert resp.status_code == 200
    assert resp.json['id'] == source_detail.id
    assert resp.json['name'] == source_detail.name
