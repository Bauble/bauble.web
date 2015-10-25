
import bottle
from bottle import request, response
import sqlalchemy as sa

from bauble import app, API_ROOT
from bauble.middleware import basic_auth
from bauble.model import Report

report_column_names = [col.name for col in sa.inspect(Report).columns]
report_mutable = [col for col in report_column_names
                  if col not in ['id'] and not col.startswith('_')]


def resolve_report(next):
    def _wrapped(*args, **kwargs):
        request.report = request.session.query(Report).get(request.args['report_id'])
        if request.report is None:
            bottle.abort(404, "Report not found")
        return next(*args, **kwargs)
    return _wrapped


@app.get(API_ROOT + "/report")
@basic_auth
def index_reports():
    return [report.json() for report in request.session.query(Report)]


@app.get(API_ROOT + "/report/<report_id:int>")
@basic_auth
@resolve_report
def get_report(report_id):
    return request.report.json()


@app.post(API_ROOT + "/report")
@basic_auth
def post_report():

    if not request.json:
        bottle.abort(400, 'The request doesn\'t contain a request body')

    # create a copy of the request data with only the columns
    data = {col: request.json[col] for col in request.json.keys()
            if col in report_mutable}

    report = Report(**data)
    request.session.add(report)
    request.session.commit()
    response.status = 201
    return report.json()


@app.route(API_ROOT + "/report/<report_id:int>", method='PATCH')
@basic_auth
@resolve_report
def patch_report(report_id):

    if not request.json:
        bottle.abort(400, 'The request doesn\'t contain a request body')

    # create a copy of the request data with only the columns that are mutable
    data = {col: request.json[col] for col in request.json.keys()
            if col in report_mutable}
    for key, value in data.items():
        setattr(request.report, key, data[key])
    request.session.commit()

    return request.report.json()


@app.delete(API_ROOT + "/report/<report_id:int>")
@basic_auth
@resolve_report
def delete_report(report_id):
    request.session.delete(request.report)
    request.session.commit()
    response.status = 204
