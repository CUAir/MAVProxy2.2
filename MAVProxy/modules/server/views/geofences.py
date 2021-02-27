from MAVProxy.modules.server.urls import app
from MAVProxy.modules.mavproxy_fence import get_fence_mod
from flask import request
from MAVProxy.modules.server.data import Data
import MAVProxy.modules.server.views.decorators as decs

import MAVProxy.mavproxy_logging

logger = MAVProxy.mavproxy_logging.create_logger("geofences")


# format [{'lat':lat, 'lon':lon}, {'lat':lat, 'lon',lon}...}]
@app.route('/v2/geofence', methods=['POST'])
@decs.trace_errors(logger, 'Failed to add geofence')
def add_fence():
        fence_data = request.get_json()
        for latlon in fence_data:
            if abs(float(latlon['lat'])) > 180 or abs(float(latlon['lon'])) > 180:
                return 'Error: waypoint lat/lon out of range', 400
        fenceMod = get_fence_mod()
        fenceMod.addFence(fence_data)
        return "Added Fence"


# format {password: 'password:, "data": [{'lat':lat, 'lon':lon}, {'lat':lat, 'lon',lon}...}]}
@app.route('/ground/api/v3/geofence', methods=['POST'])
@decs.trace_errors(logger, 'Failed to add geofence')
def add_fence3():
    try:
        fence_data = request.get_json()
    except:
        return "Error: data is not json", 400
    try:
        token = request.headers.get('token')
    except:
        return "Error: wrong headers", 400
    if token != Data.password:
        logger.error("TOKEN IS " + str(token))
        return "Error: Invalid token: "+token, 400
    
    for latlon in fence_data:
        if(abs(float(latlon['lat'])) > 180 or abs(float(latlon['lon'])) > 180):
            return 'Error: waypoint lat/lon out of range', 400
    fenceMod = get_fence_mod()
    fenceMod.addFence(fence_data)
    return "Added Fence"

@app.route('/ground/api/v3/geofence', methods=['GET'])
@app.route('/v2/geofence', methods=['GET'])
@decs.trace_errors(logger, 'Failed to get geofence')
def get_fence():
    fenceMod = get_fence_mod()
    return str(fenceMod.getFence())


