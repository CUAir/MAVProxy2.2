from MAVProxy.modules.server.urls import app
from MAVProxy.modules.server.data import Data
from MAVProxy.modules.mavproxy_sda.sda_engine import get_sda_mod
from MAVProxy.modules.mavproxy_sda.sda_util import Convert
from MAVProxy.modules.mavproxy_database import get_db_mod
from MAVProxy.modules.mavproxy_wp import get_wp_mod
from MAVProxy.modules.mavproxy_obstacle_prediction.obstacle_prediction import get_sda_obst_pred_mod
import MAVProxy.modules.server.views.decorators as decs
from MAVProxy.modules.mavproxy_plane_prediction.plane_prediction import get_sda_plane_pred_mod
from traceback import format_exc
from flask import request
import json

import MAVProxy.mavproxy_logging

logger = MAVProxy.mavproxy_logging.create_logger("sda")

@app.route('/ground/api/v3/sda_obst_state')
def get_sda_obst_state():
    if not get_sda_obst_pred_mod().check_precondition():
        return "Not enough data points to generate predictive model", 412
    #return prediction_module.function_in_other_file()
    return get_sda_obst_pred_mod().get_obst_state()


@app.route('/ground/api/v3/sda_plane_state')
@decs.trace_errors(logger, "Failed to get plane state")
def get_sda_plane_state():
    if not get_sda_plane_pred_mod().check_precondition():
        return "Not enough waypoints or plane data to generate predictive model", 412
    return get_sda_plane_pred_mod().get_plane_state()

@app.route('/ground/api/v3/sda')
def get_sda_enabled():
    try:
        return json.dumps(get_sda_mod().sda_enabled())
    except:
        logger.error('Error: no SDA module available')
        return 'Error: no SDA module available', 500


@app.route('/ground/api/v3/sda', methods=['POST'])
def start_sda2():
    try:
        try:
            token = request.headers.get('token')
        except:
            logger.error("Error: wrong headers for sda activation")
            return "Error: wrong headers", 500
        if token != Data.password:
            logger.error("Error: wrong auth token for sda activation")
            return "Error: Invalid token", 500

        get_sda_mod().enable_sda()
        return json.dumps(True)
    except:
        logger.error('Error: Unable to start SDA (may already be running)')
        return 'Error: Unable to start SDA (may already be running)', 500


@app.route('/ground/api/v3/sda', methods=['DELETE'])
def stop_sda2():
    try:
        try:
            token = request.headers.get('token')
        except:
            logger.error("Error: wrong headers for SDA termination")
            return "Error: wrong headers", 500
        if token != Data.password:
            logger.error("Error: wrong auth token for SDA termination")
            return "Error: Invalid token", 500

        waypoints = get_db_mod().get_waypoints()
        print([w['sda'] for w in waypoints])
        waypoints = [w for w in waypoints if not w['sda']]
        print([w['sda'] for w in waypoints])
        get_wp_mod().wp_add_list(waypoints)
        get_sda_mod().disable_sda()
        
        return json.dumps(True)
    except:
        logger.error('Error: Unable to delete SDA waypoints')
        logger.error(format_exc())
        return 'Error: Unable to delete SDA waypoints', 500
 