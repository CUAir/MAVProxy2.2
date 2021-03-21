import json

import mavproxy_logging
import modules.server.views.decorators as decs

from pymavlink.mavutil import mavlink
from modules.server.data import Data
from modules.server.urls import app
from modules.mavproxy_wp import get_wp_mod
from modules.mavproxy_database import get_db_mod
# from modules.mavproxy_sda.sda_engine import get_sda_mod
from modules.mavproxy_mission import get_mission_mod
import modules.server.views.schemas as schemas
from flask import request

SECONDS_2_MILLSECONDS = 1 / 1000.0

logger = mavproxy_logging.create_logger("waypoint_api")


# Get waypoints.
@app.route('/ground/api/v3/wp', methods=['GET'])
@decs.trace_errors(logger, 'Waypoint GET failed')
@decs.get_value('wpnum', int, optional=True)
@decs.get_value('tm', float, optional=True)
def wp(wpnum, tm):
    if tm is not None:
        tm = tm * SECONDS_2_MILLSECONDS

    waypoints = get_db_mod().get_waypoints(tm)
    min_dists = get_mission_mod().get_min_dists()

    # On the frontend, the lat and lon for DO_JUMP waypoints are treated
    # as the index and count arguments, while on the backend and on
    # ArduPlane, lat and lon are ignored and param1 and param2 are the
    # arguments. Thus, we copy them over when sending them to the frontend
    for i, wp in enumerate(waypoints):
        if i < len(min_dists):
            wp['min_dist'] = min_dists[i]
        if wp['command'] == mavlink.MAV_CMD_DO_JUMP:
            wp['lat'] = wp['param1']
            wp['lon'] = wp['param2']
            wp['min_dist'] = 0

    if wpnum is None:
        return json.dumps(list(waypoints))

    if wpnum >= 0 and wpnum < len(get_db_mod().wps):
        return json.dumps(waypoints[wpnum])


# Add a new waypoint.
@app.route('/ground/api/v3/wp', methods=['POST'])
@decs.trace_errors(logger, 'Waypoint POST failed')
@decs.require_headers({'token': Data.password})
@decs.validate_json(logger, schemas.waypoint_or_waypointlist)
def wp_add(wp_or_wplist):
    # Do bulk upload
    if type(wp_or_wplist) is list:
        wp_list = wp_or_wplist
        for waypoint in wp_list:
            waypoint['index'] = -1
        get_wp_mod().wp_send_list(wp_list)
        return 'true', 200
    wp = wp_or_wplist
    print ("wpl length: " + str(len(wp)))
    get_wp_mod().wp_insert(wp, wp['index'])
    return 'true', 200


# Update a single waypoint.
@app.route('/ground/api/v3/wp', methods=['PUT'])
@decs.trace_errors(logger, 'Waypoint PUT failed')
@decs.require_headers({'token': Data.password})
@decs.validate_json(logger, schemas.waypoint_or_waypointlist)
def wp_update(wp):
    get_wp_mod().wp_update(wp, wp['index'])
    return 'true', 200


# Delete a single waypoint.
@app.route('/ground/api/v3/wp', methods=['DELETE'])
@decs.trace_errors(logger, 'Waypoint DELETE failed')
@decs.require_headers({'token': Data.password})
@decs.get_value('wpnum', int)
def wp_delete_single(wpnum):
    if wpnum >= len(get_db_mod().wps):
        logger.error('Error: index out of bounds. There are currently only {} waypoints'.format(len(get_db_mod().wps)))
        return 'Error: index out of bounds. There are currently only {} waypoints'.format(len(get_db_mod().wps)), 400
    get_wp_mod().wp_remove(wpnum)
    return "Deleting waypoint"


# Get an SDA waypoint between start_index and end_index.
# @app.route('/ground/api/v3/wp/sda', methods=['GET'])
# @decs.trace_errors(logger, 'Waypoint sda GET failed')
# @decs.get_value('start_index', int)
# @decs.get_value('end_index', int)
# def wp_sda(start_index, end_index):
#     path = get_sda_mod().get_sda_suggestions(min(start_index, end_index), max(start_index, end_index))
#     return json.dumps(path)


# Replace all waypoints with a new list of waypoints
@app.route('/ground/api/v3/wp/replace', methods=['DELETE'])
@decs.trace_errors(logger, 'Waypoint replace failed')
@decs.require_headers({'token': Data.password})
def wp_replace():
    logger.info("in wp replce")
    # Clear all waypoints
    get_wp_mod().wp_clear()
    # Insert list of waypoints
    wp_add()
    return "Success", 200


# Get the index of current waypoint.
@app.route('/ground/api/v3/current', methods=['GET'])
@decs.trace_errors(logger, 'Get current failed')
def wp_current():
    return get_db_mod().get_current_wp()


# Set the current waypoint to index.
# {'current': '1'}
@app.route('/ground/api/v3/current', methods=['POST'])
@decs.trace_errors(logger, 'Set current failed')
@decs.require_headers({'token': Data.password})
@decs.validate_json(logger, schemas.current)
def wp_set_current(current):
    desired_index = current['current']
    if (desired_index >= len(get_db_mod().wps)):
        return 'Error: Desired index out of range', 400

    get_wp_mod().wp_set_current(desired_index)

    return "Attempting to update current", 200


# Get a list of splines the plane is trying to fly.
@app.route('/ground/api/v3/wp/splines', methods=['GET', 'DELETE'])
@decs.trace_errors(logger, 'Get splines failed')
def wp_splines():
    if request.method == "GET":
        output = {'splines': get_mission_mod().spline_path}
        return json.dumps(output)
    elif request.method == "DELETE":
        get_mission_mod().clear_splines()
        return "Success", 200
    else:
        logger.error("Invalid method:" + str(request.method))
        return "Invalid method: " + str(request.method), 400


@app.route('/ground/api/v3/wp/refresh', methods=['PUT'])
@decs.trace_errors(logger, 'Refresh waypoints failed')
def wp_refresh():
    get_wp_mod().fetch()
    return json.dumps(True)
