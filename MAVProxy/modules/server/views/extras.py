from MAVProxy.modules.server.urls import app
from MAVProxy.modules.mavproxy_mode import get_mode_mod
from MAVProxy.modules.mavproxy_arm import get_arm_mod
from MAVProxy.modules.mavproxy_misc import get_misc_mod
from MAVProxy.modules.server.data import Data
import MAVProxy.modules.server.views.decorators as decs
from flask import request
import json
import MAVProxy.modules.server.mapcache as mapcache
import MAVProxy.mavproxy_logging

logger = MAVProxy.mavproxy_logging.create_logger("extras")


@app.route('/ground/api/v3/cachemaps', methods=['POST'])
@decs.trace_errors(logger, 'Failed to add location')
def cachemaps():
    logger.info("Location add request received")
    json = request.get_json()
    if 'name' not in json.keys() or 'lat' not in json.keys() or 'lng' not in json.keys():
        return 'Error: Invalid POST format', 400
    newJSON = mapcache.cacheLocation(json['name'], json['lat'], json['lng'], json['zoom'] if 'zoom' in json.keys() else 17)
    logger.info("Location Added")
    return newJSON



@app.route('/ground/api/v3/getlocations', methods=['GET'])
@decs.trace_errors(logger, 'Failed to get locations')
def getlocations():
    return mapcache.getLocations()



@app.route('/ground/api/v3/arm', methods=['POST'])
@decs.trace_errors(logger, 'Plane failed to arm')
def arm():
    try:
        confirm = request.headers.get('confirm')
        token = request.headers.get('token')
    except Exception:
        return "Error: wrong headers", 400
    if token != Data.password:
        return "Error: Invalid token", 401
    if confirm != 'confirm':
        return "Error: no confirm header", 400

    get_arm_mod().set_arm()
    logger.info('Plane armed')
    return "Plane armed successfully"


@app.route('/ground/api/v3/arm', methods=['DELETE'])
@decs.trace_errors(logger, 'Plane failed to disarm')
def disarm():
    try:
        confirm = request.headers.get('confirm')
        token = request.headers.get('token')
    except Exception:
        return "Error: wrong headers", 400
    if token != Data.password:
        return "Error: Invalid token", 401
    if confirm != 'confirm':
        return "Error: no confirm header", 400

    get_arm_mod().set_disarm()
    logger.info('Plane disarmed')
    return "Plane disarmed successfully"


# USAGE: POST json with 'mode'  = 'RTL'
@app.route('/ground/api/v3/set_mode', methods=['POST', 'OPTIONS'])
@decs.trace_errors(logger, 'Failed to set mode')
def set_mode():
    modes = ['RTL', 'TRAINING', 'LAND', 'AUTOTUNE', 'STABILIZE', 'AUTO', 'GUIDED',
             'LOITER', 'MANUAL', 'FBWA', 'FBWB', 'CRUISE', 'INITIALISING', 'CIRCLE', 'ACRO']
    
    try:
        data = request.get_json()
    except:
        return "Error: JSON cannot be read"
    try:
        token = request.headers.get('token')
    except:
        return "Error: wrong headers"
    if token != Data.password:
        return "Error: Invalid token: " + str(token)

    mode = data['mode']
    if mode not in modes:
        return "Error: Invalid mode", 400
    get_mode_mod().set_mode(mode)
    return "Accepted mode change", 200


@app.route('/ground/api/v3/flight_mode')
@decs.trace_errors(logger, 'Failed to get plane mode')
def flight_mode():
    try:
        return json.dumps(Data.pdata['FLIGHT_MODE'])
    except Exception:
        return 'MAV'


@app.route('/ground/api/v3/reboot', methods=['POST'])
@decs.trace_errors(logger, 'Failed to reboot plane')
def reboot():   
    try:
        confirm = request.headers.get('confirm')
        token = request.headers.get('token')
    except Exception:
        return "Error: wrong headers"
    if token != Data.password:
        return "Error: Invalid token"
    if confirm != 'confirm':
        return "Error: no confirm header"

    get_misc_mod().cmd_reboot("")
    return "Reboot request successful"
