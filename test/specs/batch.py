from flask import json

from faker import Faker

faker = Faker()

def test_batch_get(client, session, family, genus):
    session.add_all([family, genus])
    session.commit()

    req = [{
        'method': 'GET',
        'relative_url': '/family/{}'.format(family.id)
    }, {
        'method': 'GET',
        'relative_url': '/genus/{}'.format(genus.id)
    }]
    resp = client.post('/batch', data=json.dumps(req), content_type='application/json')
    assert resp.status_code == 207
    resp0 = json.loads(resp.json[0]['body'])
    assert resp0['id'] == family.id
    print('resp.json: ', resp.json)


def test_batch_error(client, session, family, genus):
    # TODO: test that if we pass in a batch operation that all of the operations fail if
    # one of them fails, this include that if we do two mutable request that if the second
    # one fails the first one doesn't succeed
    session.add_all([family, genus])
    session.commit()

    req = [{
        'method': 'GET',
        'relative_url': '/family/{}'.format(faker.pyint())
    }, {
        'method': 'GET',
        'relative_url': '/family/{}'.format(family.id)
    }]
    resp = client.post('/batch', data=json.dumps(req), content_type='application/json')
    assert resp.status_code == 404
    assert len(resp.json) == 1
    # resp0 = json.loads(resp.json[0]['body'])
    # assert resp0['id'] == family.id



def test_batch_rollback(client, session, family, genus):
    """If a batch fails then previous changes should rollback.
    """
    session.add_all([family, genus])
    session.commit()

    original_name = family.family

    req = [{
        'method': 'PATCH',
        'relative_url': '/family/{}'.format(family.id),
        'body': json.dumps({'family': faker.pystr()})
    }, {
        'method': 'DELETE',
        'relative_url': '/family/{}'.format(faker.pyint())
    }]
    resp = client.post('/batch', data=json.dumps(req), content_type='application/json')
    assert resp.status_code == 404
    print('resp.json: ', resp.json)
    assert len(resp.json) == 2

    session.add(family)
    session.refresh(family)
    assert family is not None
    assert family.family == original_name
