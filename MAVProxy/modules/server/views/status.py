from MAVProxy.modules.server.urls import app
from MAVProxy.modules.server.data import Data
import json
import time
import traceback
import re

from flask import request
from views_utils import json_serial
import MAVProxy.modules.server.views.decorators as decs

from MAVProxy.modules.mavproxy_database import get_db_mod
from MAVProxy.modules.mavproxy_mission import get_mission_mod
import MAVProxy.modules.server.views.decorators as decs
from MAVProxy.modules.mavproxy_plane_prediction.plane_prediction import get_sda_plane_pred_mod
import MAVProxy.mavproxy_logging

logger = MAVProxy.mavproxy_logging.create_logger("status")


# Can anyone think of a cleaner way to do this?
mpstate = get_db_mod().mpstate
if mpstate.airapi:
    base_url = "/air/api/v3/status"
else:
    base_url = "/ground/api/v3/status"


###################
#
#
#    Logic
#
#
####################

def airspeed(tm=None):
    return get_db_mod().get_vfr_hud(tm)


def attitude(tm=None):
    return get_db_mod().get_attitude(tm)


def battery(tm=None):
    return get_db_mod().get_sys_status(tm)


def climb(tm=None):
    try:
        return get_db_mod().get_vfr_hud(tm)['climb']
    except TypeError:  # no data, return None
        return None


def flight_time(tm=None):
    return get_db_mod().get_flight_time(tm)

def gps(tm=None):
    return get_db_mod().get_gps(tm)


def gps_status(tm=None):
    return get_db_mod().get_gps_status(tm)


def mav_info(tm=None):
    try:
        return get_db_mod().get_status_text()['info_text']
    except Exception as e:
        traceback.print_exc()
        print str(e)


def mav_warning(tm=None):
    return get_db_mod().get_status_text()['warning_text']


def mav_error(tm=None):
    return get_db_mod().get_status_text()['error_text']


def signal(tm=None):
    return get_db_mod().get_signal(tm)


def throttle(tm=None):
    try:
        return get_db_mod().get_vfr_hud(tm)['throttle']
    except TypeError:  # No data, return None
        return None


def wind(tm=None):
    return get_db_mod().get_wind(tm)


def current_wp(tm=None):
    return get_db_mod().get_current_wp(tm)


def mode(tm=None):
    return get_db_mod().get_mode(tm)

def camera_feedback(tm=None):
    return get_db_mod().get_camera_feedback(tm)

##############################
# tm UNSUPPORTED FUNCTIONS #
##############################


def armed(tm=None):
    return Data.armed


@app.route(base_url + '/powerboard')
@decs.trace_errors(logger, 'Failed to send powerboard')
def powerboard_url():
    return 'No data'


def link(tm=None):
    plane_link = False
    links = []
    # mpstate isn't particular to the database module; this is just the most convenient
    # way to access it as status isn't a subclass of MPModule
    for n, link in enumerate(get_db_mod().mpstate.mav_master):
        try:
            device = link.device
        except AttributeError:
            # This is here because I added the device in link add
            # a quick check seems to confirm that links aren't added anywhere
            # else but I want to play it safe
            device = "unknown"
        # regex is for IP-address
        if device.startswith('udp') or device.startswith('tcp') or re.match('[0-9]{0,3}((.[0-9]){0,3}){3}:[0-9]{4,5}', device) is not None:
            device_name = 'WiFi'
        elif device.startswith('/dev/tty'):
            device_name = 'Radio'
        else:
            device_name = 'Unknown'
        linkdelay = (get_db_mod().status.highest_msec - link.highest_msec) * 1.0e-3
        packet_loss = 100 if link.linkerror else link.packet_loss()
        links.append({
            "num": n + 1,
            "alive": not link.linkerror,
            "packet_loss": packet_loss,
            "num_lost": link.mav_loss,
            "link_delay": linkdelay,
            "device": device,
            "device_name": device_name,
        })
    if 'HEARTBEAT' in Data.pdata and 'LINK' in Data.pdata:
        heartbeat_link = time.time() - Data.pdata['HEARTBEAT'] < 2
        plane_link = Data.pdata['LINK'] and heartbeat_link

    return {'gps_link': Data.have_gps_lock, 'plane_link': plane_link, 'links': links}


def safe(tm=None):
    if Data.safe == 0:
        return False
    return True


def wp_count(tm=None):
    return int(len(Data.wplist))


###################
#
#
#    Routing
#
#
####################

def get_historical_status_value(func, t):
    if t is not None:
        try:
            tm = float(t) / 1000.0
        except ValueError as e:
            logger.error(str(e))
            return "invalid time argument", 300
    else:
        tm = None
    try:
        result = func(tm)
        if result is not None:
            return json.dumps(result, default=json_serial)
        else:
            return "No Content", 204
    except Exception as e:
        if isinstance(x, ValueError) and str(e) == "Database query not supported in AirAPI mode":
            return "Database query not supported in AirAPI mode", 400
        logger.error("Error in function: " + func.__name__ + "\n" + str(e))
        return "Mavproxy query error", 500


@app.route(base_url + '/progress', methods=['GET'])
@decs.trace_errors(logger, 'Failed to send progress')
def flight_progress():
    progress = get_mission_mod().get_progress()
    return json.dumps(progress)


@app.route(base_url + '/airspeed')
@decs.trace_errors(logger, 'Failed to send airspeed')
def airspeed_url():
    return get_historical_status_value(airspeed, request.args.get('tm'))


@app.route(base_url + '/attitude')
@decs.trace_errors(logger, 'Failed to send attitude')
def attitude_url():
    return get_historical_status_value(attitude, request.args.get('tm'))


@app.route(base_url + '/armed')
@decs.trace_errors(logger, 'Failed to send armed')
def armed_url():
    return get_historical_status_value(armed, request.args.get('tm'))


@app.route(base_url + '/battery')
@decs.trace_errors(logger, 'Failed to send battery')
def battery_url():
    return get_historical_status_value(battery, request.args.get('tm'))


@app.route(base_url + '/current_wp')
@decs.trace_errors(logger, 'Failed to send current_wp')
def current_wp_url():
    return get_historical_status_value(current_wp, request.args.get('tm'))


@app.route(base_url + '/climb')
@decs.trace_errors(logger, 'Failed to send climb')
def climb_url():
    return get_historical_status_value(climb, request.args.get('tm'))


@app.route(base_url + '/flight_time')
@decs.trace_errors(logger, 'Failed to send flight_time')
def flight_time_url():
    return get_historical_status_value(flight_time, request.args.get('tm'))


@app.route(base_url + '/gps')
@decs.trace_errors(logger, 'Failed to send gps')
def gps_url():
    return get_historical_status_value(gps, request.args.get('tm'))

@app.route(base_url + '/gps/prediction')
@decs.trace_errors(logger, 'Failed to send gps/prediction')
def gps_prediction_url():
    tm = time.time() + float(request.args.get('tm'))
    return get_sda_plane_pred_mod().gps_prediction(tm)

@app.route(base_url + '/gps_status')
@decs.trace_errors(logger, 'Failed to send gps_status')
def gps_status_url():
    return get_historical_status_value(gps_status, request.args.get('tm'))


@app.route(base_url + '/link')
@decs.trace_errors(logger, 'Failed to send link')
def link_url():
    return get_historical_status_value(link, request.args.get('tm'))


@app.route(base_url + '/mode')
@decs.trace_errors(logger, 'Failed to send mode')
def mode_url():
    return get_historical_status_value(mode, request.args.get('tm'))


@app.route(base_url + '/safe')
@decs.trace_errors(logger, 'Failed to send safe')
def safe_url():
    return get_historical_status_value(safe, request.args.get('tm'))


@app.route(base_url + '/signal')
@decs.trace_errors(logger, 'Failed to send signal')
def signal_url():
    return get_historical_status_value(signal, request.args.get('tm'))


@app.route(base_url + '/throttle')
@decs.trace_errors(logger, 'Failed to send throttle')
def throttle_url():
    return get_historical_status_value(throttle, request.args.get('tm'))


@app.route(base_url + '/wind')
@decs.trace_errors(logger, 'Failed to send wind')
def wind_url():
    return get_historical_status_value(wind, request.args.get('tm'))


@app.route(base_url + '/wp_count')
@decs.trace_errors(logger, 'Failed to send wp_count')
def wp_count_url():
    return get_historical_status_value(wp_count, request.args.get('tm'))


@app.route(base_url + '/mav_info')
@decs.trace_errors(logger, 'Failed to send mav_info')
def mav_info_url():
    return get_historical_status_value(mav_info, request.args.get('tm'))


@app.route(base_url + '/mav_warning')
@decs.trace_errors(logger, 'Failed to send mav_warning')
def mav_warning_url():
    return get_historical_status_value(mav_warning, request.args.get('tm'))


@app.route(base_url + '/mav_error')
@decs.trace_errors(logger, 'Failed to send mav error')
def mav_error_url():
    return get_historical_status_value(mav_error, request.args.get('tm'))


@app.route(base_url + '')
@decs.trace_errors(logger, 'Failed to send status data')
def software_status():
    if request.args.get('tm') is not None:
        try:
            tm = float(request.args.get('tm')) / 1000.0
        except ValueError:
            return "invalid time argument", 300
    else:
        tm = None

    return json.dumps({'attitude': attitude(tm),
                       'battery': battery(tm),
                       'link': link(tm),
                       'gps': gps(tm),
                       'airspeed': airspeed(tm),
                       'wind': wind(tm),
                       'throttle': throttle(tm),
                       'wp_count': wp_count(tm),
                       'current_wp': current_wp(tm),
                       'mode': mode(tm),
                       'armed': armed(tm),
                       'mav_info': mav_info(tm),
                       'mav_warning': mav_warning(tm),
                       'mav_error': mav_error(tm),
                       'gps_status': gps_status(tm),
                       'signal': signal(tm),
                       'safe': safe(tm)}, default=json_serial)


@app.route(base_url + '/geotag_data', methods=['GET'])
@decs.trace_errors(logger, "failed to retrieve geotag data")
def geotag_data():
    if request.args.get('tm') is not None:
        try:
            tm = float(request.args.get('tm')) / 1000.0
        except ValueError:
            return "invalid time argument", 300
    else:
        tm = None
    #image_data = camera_feedback(tm)
    #if image_data is None:
    #    return json.dumps(None)
    image_data = {'attitude':{'roll':0, 'pitch':0, 'yaw':0}, 'gps':{'lat':0, 'lon':0, 'rel_alt':0}}
    image_data['attitude'] = attitude(tm)
    image_data['gps'] = gps(tm)
    #image_data['attitude']['roll'] = image_data['roll']
    #image_data['attitude']['pitch'] = image_data['pitch']
    #image_data['attitude']['yaw'] = image_data['yaw']
    #image_data['gps']['lat'] = image_data['lat']
    #image_data['gps']['lon'] = image_data['lon']
    #image_data['gps']['rel_alt'] = image_data['alt_rel']
    return json.dumps(image_data)
