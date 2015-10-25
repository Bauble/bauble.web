def test_index_family(client, session, family):
    session.add(family)
    session.commit()
    resp = client.get('/api/family')
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == family.id
