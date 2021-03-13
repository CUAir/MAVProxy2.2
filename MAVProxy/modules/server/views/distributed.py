import mavproxy_logging
from modules.server.urls import app
from modules.mavproxy_distributed import get_distributed_mod
from modules.mavproxy_coverage.coverage_engine import get_coverage_mod
from modules.mavproxy_gimbal import get_gimbal_mod

import modules.server.views.decorators as decs
import flask
from flask import request
import json

logger = mavproxy_logging.create_logger("distributed")


@app.route('/ground/api/v3/distributed', methods=['POST'])
@decs.trace_errors(logger, "failed to start the distributed server")
def start_stop():
    if request.method == 'POST':
        try:
            j = request.get_json()
        except:
            return "Error: JSON cannot be read", 400
        if 'url' not in j.keys() or 'username' not in j.keys() or 'password' not in j.keys():
            return "Error: invalid POST format", 400

        try:
            with open(get_distributed_mod().get_server_file(), 'w+') as server_file:
                server_file.write(json.dumps(j))
        except:
            logger.error('Error: unable to save distributed data')

        d_username = json.dumps(j)
        if get_distributed_mod().start(True, j['url'], j['username'], j['password'], False):
            return 'Success', 200
        else:
            return 'Distributed server failed to start', 400


@app.route('/ground/api/v3/distributed/target_data')
@decs.trace_errors(logger, "failed to get target data")
def get_images():
    return json.dumps(get_distributed_mod().get_image_data())


@app.route('/ground/api/v3/distributed/gimbal', methods=['GET', 'POST', 'DELETE'])
@decs.trace_errors(logger, "Failed to retrieve, set, or reset gimbal state")
def gimbal():
    if request.method == 'GET':
        if get_distributed_mod().server_active():
            try:
                return json.dumps(get_distributed_mod().get_mode())
            except:
                return 'Error: could not retrieve gimbal mode', 500
        else:
            return "Error: Server is not active", 200
    elif request.method == 'POST':
        try:
            j = request.get_json()
        except:
            return "Error: JSON cannot be read", 400
        if 'lat' not in j.keys() or 'lon' not in j.keys():
            return "Error: invalid POST format", 400
        try:
            if not get_distributed_mod().point_gimbal(j):
                return "Error: failed to point gimbal", 500
            else:
                return "Success", 200
        except:
            return "Error: failed to point gimbal", 500
    else: # request.method == DELETE
        try:
            if not get_distributed_mod().reset_gimbal():
                return "Error: failed to reset gimbal", 500
            else:
                return "Success", 200
        except:
            return "Error: failed to reset gimbal", 500


@app.route('/ground/api/v3/distributed/regions', methods=['GET'])
@decs.trace_errors(logger, "failed to retrieve mdlc and adlc info")
def regions():
    if get_distributed_mod().server_active():
        try:
            return json.dumps({
                "mdlc": get_distributed_mod().get_priority_regions(),
                "adlc": get_distributed_mod().get_adlc_targets()
            })
        except:
            return 'Error: could not retrieve priority regions from server', 500
    else:
        return "Error: Server is not active", 200


@app.route('/ground/api/v3/distributed/airdrop', methods=['GET'])
@decs.trace_errors(logger, "failed to airdrop settings")
def airdrop_settings():
    return json.dumps(get_distributed_mod().airdrop_settings())


@app.route('/ground/api/v3/distributed/gimbal_status', methods=['POST'])
@decs.trace_errors(logger, "failed to receive/set gimbal status")
def receive_gimbal_status():
    get_distributed_mod().gimbal_mode = flask.request.get_json()['mode']
    return "Success", 200


@app.route('/ground/api/v3/distributed/mdlc', methods=['POST'])
@decs.trace_errors(logger, "failed to receive/set mdlc data")
def receive_mdlc():
    get_distributed_mod().priority_regions = flask.request.get_json()
    return "Success", 200


@app.route('/ground/api/v3/distributed/adlc', methods=['POST'])
@decs.trace_errors(logger, "failed to receive/set gimbal adlc data")
def receive_adlc():
    get_distributed_mod().adlc_targets = flask.request.get_json()
    return "Success", 200


@app.route('/ground/api/v3/distributed/geotag', methods=['POST'])
@decs.trace_errors(logger, "failed to receive/set geotag targets")
def receive_geotag():
    image_data = flask.request.get_json()
    image_data['imageUrl'] = image_data['url']
    for corner in ['topLeft', 'bottomLeft', 'bottomRight', 'topRight']:
        image_data[corner]['lat'] = image_data[corner]['latitude']
        image_data[corner]['lon'] = image_data[corner]['longitude']
    color = "gray" if image_data['mode'] == "FIXED" else "pink"
    get_distributed_mod().image_data.append(image_data)
    get_coverage_mod().picture_add_coverage(image_data, color=color)
    return "Success", 200


@app.route('/ground/api/v3/distributed/airdrop', methods=['POST'])
@decs.trace_errors(logger, 'failed to receive/set airdrop settings')
def receive_airdrop():
    get_distributed_mod().airdrop = flask.request.get_json()
    return "Success", 200

@app.route('/ground/api/v3/distributed/camera/mode', methods=['POST'])
@decs.trace_errors(logger, 'failed to receive/set camera gimbal mode')
def set_camera_mode():
    data = flask.request.get_json()
    if data.get('mode', 'fixed') == 'fixed':
        get_gimbal_mod().set_gimbal_mode_idle()
    else:
        response = get_distributed_mod().set_camera_mode(data)
        if response !=  200:
            return "Error: failed to set camera mode", response
    return "Success", 200


