from flask_socketio import emit
import waypoints
import status
from MAVProxy.modules.server.urls import socketio
from MAVProxy.modules.server.urls import app
from MAVProxy.modules.server.data import Data

import MAVProxy.mavproxy_logging

logger = MAVProxy.mavproxy_logging.create_logger("sockets")

'''mode'''
'''mav_status/calibration'''

@socketio.on_error()
def on_error():
    logger.error('SocketIO Error')

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##             
#                                   Parameters                                #
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

def serve_parameter(name, value):
    with app.test_request_context('/'):
        socketio.emit('parameter', {"name": name, "value": value}, namespace='/socket')

def serve_max_parameter_number(number):
    with app.test_request_context('/'):
        socketio.emit('parameter.max', {"max": number}, namespace='/socket')

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##             
#                                   Waypoints                                 #
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

def serve_waypoints():
    with app.test_request_context('/'):
        socketio.emit('waypoints', waypoints.getAll(), namespace='/socket')

def serve_current():
    with app.test_request_context('/'):
        socketio.emit('current', Data.currentWPIndex , namespace='/socket')

@socketio.on('count', namespace='/socket')
def count(count):
    if not (int(count) == len(Data.wplist)):
        serve_waypoints()

@socketio.on('current', namespace='/socket')
def current(current):
    if not (int(current) == Data.currentWPIndex):
        serve_current()


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
#                                     Status                                  #
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

@socketio.on('connect', namespace='/socket')
def connect():
    logger.info("Client Connected!")
    emit('ServerMessage', {'data': 'Connected'})

def serve_vfr_hud():
    with app.test_request_context('/'):
        socketio.emit('status.airspeed', status.airspeed(), namespace='/socket')
        socketio.emit('status.throttle', status.throttle(), namespace='/socket')


def serve_attitude():
    with app.test_request_context('/'):
      socketio.emit('status.attitude', status.attitude(), namespace='/socket')


def serve_sys_status():
    with app.test_request_context('/'):
        socketio.emit('status.battery', status.battery(), namespace='/socket')


def serve_gps_raw_int():
    with app.test_request_context('/'):
        socketio.emit('status.link', status.link(), namespace='/socket')


def serve_global_position_int():
    with app.test_request_context('/'):
        socketio.emit('status.gps', status.gps(), namespace='/socket')


def serve_wind():
    with app.test_request_context('/'):
        socketio.emit('status.wind', status.wind(), namespace='/socket')

def serve_armed():
    with app.test_request_context('/'):
        logger.error(str('armed is', status.armed()))
        socketio.emit('status.armed', status.armed(), namespace='/socket')

def serve_disconnect():
    logger.warning('disconnect')
    with app.test_request_context('/'):
        socketio.emit('status.disconnect', str(True), namespace='/socket')



##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##             
#                                   Mode                                     #
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
def serve_mode(mode):
    with app.test_request_context('/'):
        socketio.emit('mode', mode, namespace='/socket')

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##             
#                                Calibration                                  #
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
def serve_calibration(text):
    with app.test_request_context('/'):
        socketio.emit('calibration', text, namespace='/socket')

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##             
#                                     Interop                                 #
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
def serve_interop_time(time):
    with app.test_request_context('/'):
        socketio.emit('interop.time', time, namespace='/socket')


def serve_interop_message(message):
    with app.test_request_context('/'):
        socketio.emit('interop.message', message, namespace='/socket')


def serve_interop_obst():
    with app.test_request_context('/'):
        socketio.emit('interop', {"obstacles": Data.pdata['obstacles'],
                                  "server_info": Data.pdata['server_info']}, namespace='/socket')


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##             
#                                     SDA                                     #
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
def serve_sda_enabled(enabled):
    with app.test_request_context('/'):
        socketio.emit('sda.enabled', enabled, namespace='/socket')