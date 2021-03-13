from modules.server.urls import app
from modules.mavproxy_calibration import get_cali_mod
from modules.mavproxy_rcsetup import get_rcsetup_mod
import modules.server.views.decorators as decs
from modules.server.data import Data
from flask import request
from flask import jsonify
import sys
import os
import traceback

import mavproxy_logging

logger = mavproxy_logging.create_logger("calibration")

@app.route('/ground/api/v3/cali/accel', methods=['POST'])
@decs.trace_errors(logger, 'Failed to start accelerometer calibration')
def accel_start():
    try:
        token = request.headers.get('token')
    except:
        return "Error: wrong headers", 400
    if token != Data.password:
        return "Error: Invalid token", 403

    get_cali_mod().start_accel_cal()
    return "Started accelerometer calibration."


@app.route('/ground/api/v3/cali/accel', methods=['PUT'])
@decs.trace_errors(logger, 'Failed to continue accelerometer calibrations')
def accel_continue():
    try:
        token = request.headers.get('token')
    except:
        return "Error: wrong headers", 400
    if token != Data.password:
        return "Error: Invalid token", 403

    get_cali_mod().continue_accel()
    return "Continuing."

        
@app.route('/ground/api/v3/cali/gyro', methods=['POST'])
@decs.trace_errors(logger, 'Failed to start gyroscope calibration')
def gyro_cal():
    try:
        token = request.headers.get('token')
    except:
        return "Error: wrong headers", 400
    if token != Data.password:
        return "Error: Invalid token", 403

    return jsonify(get_cali_mod().do_gyro_calibration())
        

@app.route('/ground/api/v3/cali/pressure', methods=['POST'])
@decs.trace_errors(logger, 'Failed to start pressure calibration')
def pressure_cal():
    try:
        token = request.headers.get('token')
    except:
        return "Error: wrong headers", 400
    if token != Data.password:
        return "Error: Invalid token", 403

    return jsonify(get_cali_mod().cal_pressure())


@app.route('/ground/api/v3/cali/rc', methods=['POST'])
@decs.trace_errors(logger, 'Failed to start rc calibration')
def rc_start():
    try:
        token = request.headers.get('token')
    except:
        print "A"
        return "Error: wrong headers", 400
    if token != Data.password:
        return "Error: Invalid token", 403

    return jsonify(get_rcsetup_mod().start_rccal())


@app.route('/ground/api/v3/cali/rc', methods=['DELETE'])
@decs.trace_errors(logger, 'Failed to stop rc calibration')
def rc_stop():
    try:
        token = request.headers.get('token')
    except:
        return "Error: wrong headers", 400
    if token != Data.password:
        return "Error: Invalid token", 403

    return jsonify(get_rcsetup_mod().end_rccal())
