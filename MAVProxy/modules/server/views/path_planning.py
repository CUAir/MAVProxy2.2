from MAVProxy.modules.server.urls import app
from MAVProxy.modules.server.data import Data
import MAVProxy.modules.server.views.decorators as decs
from traceback import format_exc
from flask import request
import json
import MAVProxy.mavproxy_logging
from MAVProxy.modules.mavproxy_path_planning.path_planning_engine import get_path_planning_mod

logger = MAVProxy.mavproxy_logging.create_logger("path_planning")

@app.route('/ground/api/v3/path_planning', methods=['POST'])
@decs.trace_errors(logger, 'Failed to reroute path')
def path_planning():
    params = request.json
    print(params)

    # breakout request body into variables
    route_wp_indices = params["route_wp_indices"]
    geofence = params["geofence"]
    buf = int(params["buffer"])

    get_path_planning_mod().plan(route_wp_indices, geofence, buf)

    return json.dumps(True)

@app.route('/ground/api/v3/path_planning/delete', methods=['DELETE'])
@decs.trace_errors(logger, 'Failed to delete wps')
def delete_sda():
    get_path_planning_mod().delete_sda_wp()
    return json.dumps(True)