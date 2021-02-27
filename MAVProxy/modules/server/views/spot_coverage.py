import MAVProxy.mavproxy_logging

from MAVProxy.modules.server.urls import app
from MAVProxy.modules.server.data import Data
import MAVProxy.modules.server.views.decorators as decs
from MAVProxy.modules.mavproxy_spot_coverage import get_spot_coverage_mod
import MAVProxy.modules.server.views.schemas as schemas
from flask import request
import json

logger = MAVProxy.mavproxy_logging.create_logger("spot_coverage")


@app.route('/ground/api/v3/coverage/search_grid', methods=['GET'])
@decs.trace_errors(logger, 'spot coverage search grid get failed')
def get_search_grid():
    return json.dumps(get_spot_coverage_mod().get_searchgrid())


@app.route('/ground/api/v3/coverage/search_grid', methods=['POST'])
@decs.trace_errors(logger, 'sport coverage search grid set failed')
@decs.require_headers({'token': Data.password})
@decs.validate_json(logger, schemas.search_grid)
def set_search_grid():
    data = request.get_json()
    get_spot_coverage_mod().set_searchgrid_data(data)
    return json.dumps(True)


@app.route('/ground/api/v3/coverage', methods=['GET'])
@decs.trace_errors(logger, 'failed to retrieve spot coverage settings')
def coverage_settings():
    return json.dumps(get_spot_coverage_mod().get_settings())


@app.route('/ground/api/v3/coverage', methods=['POST'])
@decs.trace_errors(logger, 'spot coverage request failed')
@decs.require_headers({'token': Data.password})
@decs.validate_json(logger, schemas.coverage_settings)
def coverage():
    data = request.get_json()
    coverage_wps = get_spot_coverage_mod().get_segments_with_settings(data)
    return json.dumps([]) if coverage_wps is None else json.dumps(coverage_wps)
