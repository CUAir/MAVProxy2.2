import json

import mavproxy_logging
import modules.server.views.decorators as decs
from modules.server.urls import app
from modules.mavproxy_coverage.coverage_engine import get_coverage_mod
import modules.server.views.schemas as schemas
import flask


logger = mavproxy_logging.create_logger("Coverage")

@app.route('/ground/api/v3/coverage')
@decs.trace_errors(logger, 'coverage version get failed')
def get_coverage():
    j = json.dumps(get_coverage_mod().version)
    return j


@app.route('/ground/api/v3/coverage', methods=['DELETE'])
@decs.trace_errors(logger, 'Failed to reset coverage image')
def reset_coverage():
    get_coverage_mod().reset_coverage()
    return "Success", 200
