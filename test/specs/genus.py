from bauble.models import Genus

def test_serializer(session, genus):
    session.add(genus)
    session.commit()
    genus_json = genus.jsonify()
    assert Genus.jsonify(genus) == genus_json
    assert 'str' in genus_json
    print('genus_json: ', genus_json)


def test_index_genus(client, session, genus):
    session.add(genus)
    session.commit()
    resp = client.get('/api/genus')
    assert resp.status_code == 200
    assert len(resp.json) == 1
    assert resp.json[0]['id'] == genus.id


def test_count(client, session, genus, taxon, accession):
    session.add_all([genus, taxon, accession])
    session.commit()
    resp = client.get('/api/genus/{}/count'.format(genus.id), query_string={
        'relation': ['/taxa', '/taxa/accessions', '/taxa/accessions/plants']
    })
    assert resp.status_code == 200, resp.data
    data = resp.json
    assert data['taxa'] == 1
