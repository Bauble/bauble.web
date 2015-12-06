from faker import Faker

from bauble.models import User

faker = Faker()

def test_serializer(session, user):
    session.add(user)
    session.commit()
    user_json = user.jsonify()
    assert User.jsonify(user) == user_json
    assert 'password' not in user_json
    assert '_password' not in user_json
