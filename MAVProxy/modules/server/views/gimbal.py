from modules.server.urls import app
from modules.mavproxy_gimbal import get_gimbal_mod
import json
from flask import request
import modules.server.views.decorators as decs

import mavproxy_logging

logger = mavproxy_logging.create_logger("gimbal")

# Can anyone think of a cleaner way to do this?
mpstate = get_gimbal_mod().mpstate
if mpstate.airapi:
    base_url = "/air/api/v3/gimbal"
else:
    base_url = "/ground/api/v3/gimbal"

@app.route(base_url + '/point', methods=['POST'])
@decs.trace_errors(logger, 'failed to set gimbal point at angle')
def set_gimbal_angle():
    angle_data = request.get_json()
    get_gimbal_mod().set_gimbal_angle(angle_data)
    return json.dumps(True)

@app.route(base_url + '/roi', methods=['POST','DELETE'])
@decs.trace_errors(logger, 'failed to update gimbal gps roi')
def update_roi():
    if request.method == "POST":
        roi_data = request.get_json()
        get_gimbal_mod().add_gps_rois(roi_data)
    else:
        #roi_id = int(request.args['id'])
        roi_id = request.get_json()["id"]
        get_gimbal_mod().deactivate_roi(roi_id)
    return json.dumps(True)

@app.route(base_url + '/mode/gps', methods=['POST'])
@decs.trace_errors(logger, 'failed to set gimbal mode gps')
def set_gimbal_mode_gps():
    get_gimbal_mod().set_gimbal_mode_gps()
    return json.dumps(True)

@app.route(base_url + '/roi/current', methods=['POST'])
@decs.trace_errors(logger, 'failed to update current gps roi target')
def update_gimbal_roi_target():
    ret = get_gimbal_mod().update_curr_roi()
    return json.dumps(ret)

@app.route(base_url + '/roi', methods=['GET'])
@decs.trace_errors(logger, 'failed to update current gps roi target')
def test_get_rois():
    # logger.error(get_gimbal_mod().test_get_rois())
    return get_gimbal_mod().test_get_rois()

@app.route(base_url + '/idle', methods=['POST'])
@decs.trace_errors(logger, 'failed to set gimbal mode to idle')
def set_gimbal_idle():
    get_gimbal_mod().set_gimbal_mode_idle()
    return json.dumps(True)

@app.route(base_url + '/off-axis', methods=['POST'])
@decs.trace_errors(logger, 'failed to point at off-axis')
def set_gimbal_off_axis():
    logger.critical('got request')
    off_axis_roi = request.get_json()
    if get_gimbal_mod().is_targetable(off_axis_roi):
        get_gimbal_mod().set_gimbal_mode_gps()
        get_gimbal_mod().cmd_gimbal_roi([off_axis_roi["gpsLocation"]["latitude"], off_axis_roi["gpsLocation"]["longitude"], off_axis_roi["alt"]])
        return json.dumps(True)
    logger.critical('finished request')
    return json.dumps(False)

