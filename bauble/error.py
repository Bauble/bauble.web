from functools import wraps
import traceback

from flask import current_app as app, render_template
import webassets
from werkzeug.exceptions import HTTPException

class BaubleError(Exception):
    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        if self.msg is None:
            return str(type(self).__name__)
        else:
            return '%s: %s' % (type(self).__name__, self.msg)
        return self.msg

class CommitException(Exception):

    def __init__(self, exc, row):
        self.row = row  # the model we were trying to commit
        self.exc = exc  # the exception thrown while committing

    def __str__(self):
        return str(self.exc)


class PermissionError(BaubleError):
    pass

class AuthenticationError(BaubleError):
    pass

class LoginError(BaubleError):
    pass

class DatabaseError(BaubleError):
    pass

class EmptyDatabaseError(DatabaseError):
    pass

class MetaTableError(DatabaseError):
    pass

class TimestampError(DatabaseError):
    pass

class RegistryError(DatabaseError):
    pass

class VersionError(DatabaseError):

    def __init__(self, version):
        super(VersionError, self).__init__()
        self.version = version


class SQLAlchemyVersionError(BaubleError):
    pass

class CheckConditionError(BaubleError):
    pass



def check(condition, msg=None):
    """
    Check that condition is true.  If not then raise
    CheckConditionError(msg)
    """
    if not condition:
        raise CheckConditionError(msg)



_error_handlers = {}

def init_errorhandlers(app):
    for code_or_exception, func in _error_handlers.items():
        app.errorhandler(code_or_exception)(func)


def errorhandler(code_or_exception):
    def _decorator(f):
        @wraps(f)
        def _wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        _error_handlers[code_or_exception] = _wrapper
        return _wrapper
    return _decorator

@errorhandler(500)
def error_handler_500(error):
    app.logger.error(error)
    if app.debug:
        return render_template('errors/500.html', error=error), 500
    else:
        return "Internal Server Error", 500


@errorhandler(Exception)
def error_handler_exc(error):
    app.log_exception(error)
    print('ERROR: {}'.format(error))
    traceback.print_exc()
    tb = traceback.format_exc()

    if isinstance(error, HTTPException):
        return error

    if app.debug:
        return render_template('errors/500.html', traceback=tb, error=error), 500
    else:
        return "Internal Server Error", 500


@errorhandler(webassets.exceptions.FilterError)
@errorhandler(webassets.exceptions.BuildError)
def webassets_filter_error(error):
    e = str(error).replace('\\n', '\n')
    return '<pre>{}</pre>'.format(e), 500


# @app.error(500)
# def default_error_handler(error):
#     # TODO: only print the error when the debug flag is set
#     # make sure the error is printed in the log

#     if response.status_code >= 400 and response.status_code <= 599:
#         print('error.status: ', error.status)
#         print('error.body: ', error.body)

#     from bauble.routes import set_cors_headers
#     set_cors_headers()
#     if isinstance(error, str):
#         return error
#     elif error.body is not None:
#         return str(error.body)
#     # TODO: returning exception is really that safe since we don't know what will be
#     # in the response text
#     # elif error.exception:
#     #     return str(error.exception)


# common_errors = [400, 403, 404, 406, 409, 415, 422, 500]
# for code in common_errors:
#     app.error(code)(default_error_handler)

# @app.error(401)
# def error_handler_401(error):
#     # set the cors headers explicity since the error handler use a fresh request
#     from bauble.routes import set_cors_headers
#     set_cors_headers()
#     if request.auth:
#         user, password = request.auth
#         return "Could not authorize user: {user}".format(user=user)
#     else:
#         return "No Authorization header."


# @app.error(409)
# def error_handler_409(error):
#     # set the cors headers explicity since the error handler use a fresh request
#     from bauble.routes import set_cors_headers
#     set_cors_headers()
#     print('error.body: ', error.body)
#     #print('error.exception: ', error.body)
#     print('error: ', error)
#     return str(error.body)
    # if isinstance(error.body, sa_exc.IntegrityError):
    #     print('error.body.orig: ', error.body.orig)
    #     # s = "{}: {}".format(error.body.orig.diag.column_name,
    #     #                     error.body.orig.diag.message_primary)
    #     # print('s: ', s)


    #     d = {
    #         'field': error.exception.orig.diag.column_name,
    #         'message': error.exception.orig.diag.message_primary
    #     }
    #     print('d: ', d)
    #     return d
    #     # return "{}: {}".format(error.body.orig.diag.column_name,
    #     #                        error.body.orig.diag.message_primary)
    # else:
    #     return str(error)


#
# 480 and up are custom response codes
#
# TODO: ** i'm not sure about these custom response codes anymore
# @app.error(480)
# def error_handler_480(error):
#     return default_error_handler("Account has not been approved")

# @app.error(481)
# def error_handler_481(error):
#     return default_error_handler("Organization account has been suspended")

# @app.error(482)
# def error_handler_482(error):
#     return default_error_handler("User account has been suspended")
