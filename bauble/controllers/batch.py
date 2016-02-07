from flask import current_app, json, Blueprint, request
from flask.ext.login import login_required
from marshmallow import Schema, fields, validate
from webargs.flaskparser import use_args

blueprint = bp = Blueprint('batch', __name__)

class RequestSchema(Schema):
    relative_url = fields.Str(required=True)
    method = fields.Str(validate=validate.OneOf(['GET', 'POST', 'PATCH', 'DELETE']),
                        missing='GET')
    body = fields.Str()

    class Meta:
        strict = True


@bp.route('/batch', methods=['POST'])
@login_required
# @use_args(RequestSchema(many=True), locations=('json',))
def batch():
    """
    Execute multiple requests, submitted as a batch.

    :statuscode 207: Multi status
    """
    requests, err = RequestSchema().load(request.get_json(), many=True)
    responses = []
    status_code = 207
    for req in requests:
        method = req['method']
        url = req['relative_url']
        body = req.get('body', None)
        headers = req.get('headers', {})

        with current_app.app_context():
            headers.setdefault('accept', 'application/json')
            with current_app.test_request_context(url, method=method, data=body,
                                                  headers=headers):
                try:
                    # Can modify flask.g here without affecting
                    # flask.g of the root request for the batch

                    # Pre process Request
                    rv = current_app.preprocess_request()

                    if rv is None:
                        # Main Dispatch
                        rv = current_app.dispatch_request()

                except Exception as e:
                    rv = current_app.handle_user_exception(e)

                response = current_app.make_response(rv)

                # Post process Request
                response = current_app.process_response(response)



        # Response is a Flask response object.
        # _read_response(response) reads response.response
        # and returns a string. If your endpoints return JSON object,
        # this string would be the response as a JSON string.
        responses.append({
            "status_code": response.status_code,
            "body": response.data.decode('utf-8'),
            "headers": [{'name': k, 'value': v} for k, v in response.headers.items()]
        })

        # if error response
        if (response.status_code % 400 < 100) or (response.status_code % 400 < 100):
            status_code = response.status_code
            break

    return json.dumps(responses), status_code
