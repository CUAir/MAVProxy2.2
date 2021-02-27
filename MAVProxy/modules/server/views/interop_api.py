import time
import pickle
import json

from flask import jsonify, request
from views_utils import json_serial

import MAVProxy.modules.mavproxy_interop.interop as interop
import MAVProxy.mavproxy_logging

from MAVProxy.modules.server.urls import app
from MAVProxy.modules.server.data import Data
from MAVProxy.modules.mavproxy_database import get_db_mod as db
import MAVProxy.modules.server.views.decorators as decs

get_interop = interop.get_instance

logger = MAVProxy.mavproxy_logging.create_logger("interop_api")


# Returns all available interop information
# "Obstacles" : Data structure containg obstacles ({"stationary_obstacles":[]})
# "server_working" : Does the server believe it is functioning correctly (boolean)
# "hz" : Rolling frequency of interop telemetry posts (integer)
# "active" : Is the server active (boolean)
@app.route('/ground/api/v3/interop')
@decs.trace_errors(logger, 'Failed to send interop data')
def get_info():
    if get_interop().server_active():
        interop_inst = get_interop()
        return json.dumps({"obstacles": interop_inst.get_obstacles(),
                           "server_working": interop_inst.is_working(),
                           "hz": interop_inst.get_rolling_frequency(),
                           "active": interop_inst.server_active(),
                           "mission_waypoints": interop_inst.get_mission_waypoints(),
                           "mission_wp_dists": interop_inst.get_wp_min_dists(),
                           "active_mission": interop_inst.get_active_mission()})
    else:
        return 'Error: Server is not active', 200


@app.route('/ground/api/v3/interop/obstacles')
@decs.trace_errors(logger, 'Failed to get interop obstacles')
def get_obstacles():
    if request.args.get('time') is not None:
        try:
            tm = float(request.args.get('time')) / 1000.0
            return json.dumps(db().get_interop_obstacles(tm), default=json_serial)
        except ValueError:
            return "invalid time argument", 300

    if get_interop().server_active():
        return json.dumps(get_interop().get_obstacles())
    else:
        return 'Error: Server is not active', 500


@app.route("/ground/api/v3/interop/hz")
@decs.trace_errors(logger, 'Failed to get interop post frequency')
def get_hz():
    if get_interop().server_active():
        return str(get_interop().get_rolling_frequency())
    else:
        return "Error: Server is not active", 200


@app.route("/ground/api/v3/interop/active")
@decs.trace_errors(logger, 'Failed to get interop server active')
def get_is_active():
    return get_interop().server_active()


@app.route("/ground/api/v3/interop/status")
@decs.trace_errors(logger, 'Failed to get interop server working')
def get_is_working():
    if get_interop().server_active():
        return str(get_interop().is_working())
    else:
        return "Error: Server is not active", 500


@app.route('/ground/api/v3/interop/setup', methods=['GET', 'POST'])
@decs.trace_errors(logger, 'Failed to add interop startup data')
def interop_url2():
    if request.method == 'GET':
        try:
            file_name = get_interop().get_login_file()
            with open(file_name, "r") as login_file:
                return jsonify(json.loads(login_file.read()))
        except:
            return "Error: failed to get login file data", 500
    try:
        token = request.headers.get('token')
    except:
        return "Error: wrong headers"
    if token != Data.password:
        return "Error: Invalid token"
    else:  # request.method == 'POST':
        try:
            j = request.get_json()
        except:
            return "Error: JSON cannot be read", 400
        if 'url' not in j.keys() or 'username' not in j.keys() or 'password' not in j.keys():
            return "Error: invalid POST format.", 400

        try:
            file_name = get_interop().get_login_file()
            get_interop().mission_id = j["mission_id"]
            with open(file_name, "w") as login_file:
                login_file.write(json.loads(j))
        except:
            return "Error: failed to write json to login file", 500

        pickle.dump(j, open("interop_url_data.pickle", "wb"))
        return "Change successful"

@app.route("/ground/api/v3/interop/mission_waypoints", methods=['GET'])
@decs.trace_errors(logger, 'Failed to get mission waypoints')
def get_mission_waypoints():
    mission_waypoints = None
    mission_waypoints = get_interop().get_mission_waypoints()
    
    if mission_waypoints != None:
        return json.dumps(mission_waypoints)
    else:
        return "Error: No mission waypoints", 204


lastRequest = 0
@app.route('/ground/api/v3/interop', methods=['POST'])
@decs.trace_errors(logger, 'Failed to start interop server')
def start2():
    global lastRequest
    try:
        token = request.headers.get('token')
    except:
        logger.error("Error: wrong headers")
        return "Error: wrong headers", 400
    if token != Data.password:
        logger.error("Error: Invalid token")
        return "Error: Invalid token", 400

    try:
        j = request.get_json()
    except:
        logger.error("json can't be read")
        return "Error: JSON cannot be read"
    try:
        file_name = get_interop().get_login_file()
        with open(file_name, "w") as login_file:
            login_file.write(json.dumps(j))
    except Exception as e:
        logger.error(str(e))
        logger.error("can't write to login file")
        return "Error: failed to write json to login file", 500

    pickle.dump(j, open("interop_url_data.pickle", "wb"))

    if time.time() - lastRequest < 0.5:
        logger.error('Error: Please wait 0.5 seconds between interop toggles')
        return 'Error: Please wait 0.5 seconds between interop toggles', 500
    elif (not get_interop().server_active()):
        lastRequest = time.time()
        status = get_interop().start([])  # Pass in an empty "args" list
        if status:
            return "True", 200
        else:
            logger.error("Server login failed - likely incorrect URL or interop server down")
            return "Server login failed - likely incorrect URL or interop server down", 500
    else:
        logger.error('Error: Server already started')
        return 'Error: Server already started', 500


@app.route('/ground/api/v3/interop', methods=['DELETE'])
@decs.trace_errors(logger, 'Failed to stop interop server')
def end2():
    global lastRequest
    try:
        token = request.headers.get('token')
    except:
        logger.error("Wrong headers, no auth token found")
        return "Wrong headers, no auth token found", 500
    if token != Data.password:
        logger.error("Bad interop token - server not started")
        return "Bad interop token - server not started", 500

    if (time.time() - lastRequest) < 0.5:
        logger.error('Error: Please wait 0.5 seconds between interop toggles')
        return 'Error: Please wait 0.5 seconds between interop toggles', 500
    elif(get_interop().server_active()):
        lastRequest = time.time()
        get_interop().stop([])  # Pass in empty args list
        return "True", 200
    else:
        logger.warning('Error: interop not started')
        return 'Error: interop not started', 500
