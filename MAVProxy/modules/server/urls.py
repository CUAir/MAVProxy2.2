#!/usr/bin/env python
from flask import Flask
from flask import redirect
from flask import request
import datetime
import os
import mavproxy_logging
import traceback
from modules.mavproxy_database import get_db_mod
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

logger = mavproxy_logging.create_logger("urls")

mpstate = get_db_mod().mpstate

# these statements must be done BEFORE url imports
app = Flask(__name__)

import views.status
import views.gimbal
if not mpstate.airapi:
    import views.interop_api
    import views.waypoints
    import views.parameters
    import views.geofences
    import views.extras
    import views.calibration
    import views.distributed
    import views.sda
    import views.coverage
    import views.spot_coverage
    import views.path_planning
    import views.simulated_coverage

class Urls(object):

    @staticmethod
    @app.route('/home')
    def home():
        return 'Welcome to the MAVProxy Web API!'

    @staticmethod
    @app.route('/')
    def redirect_gcs2():
        if not mpstate.airapi:
            return redirect('/static/index.html')
        else:
            return "Front end not available over AirAPI"

    @staticmethod
    @app.route('/static/<path:filename>')
    def send_file(filename):
        try:
            response = app.send_static_file(str(filename))
            response.headers["Cache-Control"] = "no-cache, no-store"
            return response
        except Exception as e:
            logger.error(str(e))

    @staticmethod
    @app.after_request
    def log_request(response):
        log_path = MAVProxy.mavproxy_logging.get_log_path()
        log_name = datetime.date.today().strftime("%d-%m-%y") + "_requests.log"
        with open(os.path.join(log_path, log_name), 'a') as log_file:
            log_file.write("{time} | ({status_code}) {source} ==> {path}\n".format(
                    time=datetime.datetime.now(),
                    status_code=response.status_code,
                    source=request.remote_addr,
                    path=request.full_path))
        return response

    def start(self):
        app.run(host='0.0.0.0', port=8001, threaded=True)
