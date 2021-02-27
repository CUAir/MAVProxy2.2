import time
import traceback
import jsonschema

from functools import wraps
from flask import request

import MAVProxy.modules.server.views.schemas as schemas

lastRequest = 0
CONCURENT_REQUEST_SPEED = 0.5  # seconds


# Try catches errors and logs them
# logs "[error_message]: error"
def trace_errors(logger, error_message):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(error_message + ": " + str(e))
                logger.error(traceback.format_exc())
                return error_message, 500
        return decorated_function
    return decorator


# header dict should be a python dictionary of the headers to require
# i.e. {'token': Data.password, 'confirm': 'confirm'}
def require_headers(header_dict):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            for key, value in header_dict.iteritems():
                if key not in request.headers:
                    return "Error: wrong headers. missins: '{}'".format(key), 403
                if request.headers.get(key) != value:
                    return "Error: wrong header value for '{}'".format(key), 403
            return func(*args, **kwargs)

        return decorated_function
    return decorator


# Asserts request format matches schema
def validate_json(logger, schema):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            json_data = request.get_json()
            try:
                schemas.jsonschema(schema).validate(json_data)
            except jsonschema.ValidationError as e:
                logger.error("JSON does contain the correct fields")
                logger.error(traceback.format_exc())
                return "Error: json does contain the correct fields: {}".format(e), 400
            return func(json_data, *args, **kwargs)

        return decorated_function
    return decorator


def get_value(value_name, vtype, optional=False):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if value_name not in request.args:
                if optional:
                    kwargs[value_name] = None
                    return func(*args, **kwargs)
                return "Error: no argument {}".format(value_name), 400
            try:
                value = vtype(request.args.get(value_name))
            except ValueError:
                return "Error: argument {} is not an {}".format(value_name, vtype), 400
            kwargs[value_name] = value
            return func(*args, **kwargs)

        return decorated_function
    return decorator
