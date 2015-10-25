from datetime import datetime, timedelta

import bottle
from bottle import request

from bauble import app, API_ROOT
import bauble.db as db
from bauble.model import Invitation, User
from bauble.utils import create_unique_token


@app.get(API_ROOT + "/invitations/<token:re:\w{32}>")
def get_invitation(token):

    json_data = {}
    session = None
    print('token: ', token)
    try:
        session = db.Session()
        invitation = session.query(Invitation).\
            filter(Invitation.token == token, Invitation.accepted is not True,
                   Invitation.token_expiration > datetime.now()).first()

        if not invitation:
            bottle.abort(404)

        json_data['invited_by'] = invitation.invited_by.email
        json_data['email'] = invitation.email
        json_data['expiration'] = invitation.token_expiration
        json_data['organization'] = invitation.organization.json()
    finally:
        if session:
            session.close()

    return json_data



@app.post(API_ROOT + "/invitations/<token:re:\w{32}>")
def accept_invitation(token):

    if 'password' not in request.json:
        bottle.abort(422, "A password is required for the new user")

    session = None
    try:
        session = db.Session()
        invitation = session.query(Invitation).filter_by(token=token).first()
        if not invitation:
            bottle.abort(404)

        invitation.accepted = True
        user = User(**{
            'email': invitation.email,
            'organization_id': invitation.organization_id,
            'password': request.json['password'],
            'last_accessed': datetime.now(),
            'access_token': create_unique_token(),
            'access_token_expiration': datetime.now() + timedelta(weeks=2)
        })
        session.add(user)
        session.commit()
        user_json = user.json()
    finally:
        if session:
            session.close()

    return user_json
