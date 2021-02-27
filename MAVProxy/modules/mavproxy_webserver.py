#!/usr/bin/env python

# Webserver module
# Creates webserver to access plane data
# November 2014

import time
import threading
import logging
from datetime import datetime

from modules.lib import mp_module
from pymavlink import mavutil
from modules.server.data import Data
from modules.server.urls import Urls
from modules.mavproxy_param import get_param_mod
import mavproxy_logging

logger = mavproxy_logging.create_logger("webserver")

GPS_COORD_EPSILON = 1e-5
ALTITUDE_EPSILON = 1e-4


instance = None

def get_webserver_module():
    if instance is None:
        raise ValueError("Webserver module has not been initialized")
    return instance


class WebServerModule(mp_module.MPModule):
    def __init__(self, mpstate):
        from MAVProxy.pymavlink import mavparm
        super(WebServerModule, self).__init__(mpstate, "webserver", "webserver module")
        self.webserver_param = mavparm.MAVParmDict()
        logging.basicConfig(filename='example.log', level=logging.DEBUG)

        if not mpstate.airapi:
            # Make sure we have the waypoints loaded
            self.mpstate.public_modules['wp'].wp_load()

        # put server in a dameon so it dies nicely
        self.server = Urls()
        serverThread = threading.Thread(target=self.server.start)
        serverThread.setDaemon(True)
        serverThread.start()
        self.in_air = False
        self.start_flying_time = 0

    # cleans parameter and stores it in Data
    def handle_param(self, m):
        name = str(m.param_id).replace('\x00', '')
        value = m.param_value
        Data.params[name] = value
        Data.max_param_num = get_param_mod().pstate.mav_param_count

    # stores the time of the last Heartbeat
    def handle_heartbeat(self, m):
        Data.pdata['HEARTBEAT'] = time.time()

    # Updates Data.num_sats and gps lock status
    def handle_raw_gps(self, m):
        Data.num_sats = m.satellites_visible
        if 'GPS_RAW_INT' in Data.pdata:
            gps_link = not ((float(Data.pdata['GPS_RAW_INT'].lat) == 0.0) and (float(Data.pdata['GPS_RAW_INT'].lon) == 0.0))
            if not (gps_link == Data.have_gps_lock):
                logger.info('gps lock change!')
                Data.have_gps_lock = gps_link

    def handle_vfr_hud(self, m):
        pass
        # flying = m.groundspeed > 3
        # if flying and not self.in_air:
        #   in_air = True
        #    self.start_flying_time = time.time()
        # elif flying and self.in_air:
        #    Data.flight_time = time.time() - self.start_flying_time
        # elif not flying and self.in_air:
        #    self.in_air = False

    # Stores the status text
    def handle_status_text(self, m):
        # DEBUG, INFO
        if m.severity <= 6:
            if not Data.pdata['INFO_TEXT'] or m.text != Data.pdata['INFO_TEXT'].text:
                Data.pdata['INFO_TEXT'] = m

        # WARNING, NOTICE
        elif m.severity in (5, 4):
            if not Data.pdata['INFO_TEXT'] or m.text != Data.pdata['WARNING_TEXT'].text:
                Data.pdata['WARNING_TEXT'] = m

        # Anything higher is either ERROR, CRITICAL, ALERT, or EMERGENCY
        elif m.severity < 4:
            if not Data.pdata['INFO_TEXT'] or m.text != Data.pdata['ERROR_TEXT'].text:
                Data.pdata['ERROR_TEXT'] = m

    # Stores various sensor information in Data
    def handle_sys_status(self, m):
        sensors = {'AS': mavutil.mavlink.MAV_SYS_STATUS_SENSOR_DIFFERENTIAL_PRESSURE,
                   'MAG': mavutil.mavlink.MAV_SYS_STATUS_SENSOR_3D_MAG,
                   'INS': mavutil.mavlink.MAV_SYS_STATUS_SENSOR_3D_ACCEL | mavutil.mavlink.MAV_SYS_STATUS_SENSOR_3D_GYRO,
                   'AHRS': mavutil.mavlink.MAV_SYS_STATUS_AHRS,
                   'RC': mavutil.mavlink.MAV_SYS_STATUS_SENSOR_RC_RECEIVER}

        for s in sensors.keys():
            bits = sensors[s]
            present = ((m.onboard_control_sensors_enabled & bits) == bits)
            healthy = ((m.onboard_control_sensors_health & bits) == bits)
            if not present:
                status = 'UNKNOWN'
            elif not healthy:
                status = 'RED'
            else:
                status = 'GREEN'
            Data.sensor_status[s] = status

    # Stores various EKF information in Data
    def handle_ekf(self, m):
        highest = 0.0
        vars = ['velocity_variance',
                'pos_horiz_variance',
                'pos_vert_variance',
                'compass_variance',
                'terrain_alt_variance']
        for var in vars:
            v = getattr(m, var, 0)
            highest = max(v, highest)
        if highest >= 1.0:
            status = 'RED'
        elif highest >= 0.5:
            status = 'ORANGE'
        else:
            status = 'GREEN'
        Data.ekf_status = status

    # Stores various hw status in Data
    def handle_hw_status(self, m):
        if m.Vcc >= 4600 and m.Vcc <= 5300:
            status = 'GREEN'
        else:
            status = 'RED'
        Data.hw_status = status

    # stores various power status in Data
    def handle_power_status(self, m):
        if m.flags & mavutil.mavlink.MAV_POWER_STATUS_CHANGED:
            status = 'RED'
        else:
            status = 'GREEN'
        status = ' PWR:'
        if m.flags & mavutil.mavlink.MAV_POWER_STATUS_USB_CONNECTED:
            status += 'U'
        if m.flags & mavutil.mavlink.MAV_POWER_STATUS_BRICK_VALID:
            status += 'B'
        if m.flags & mavutil.mavlink.MAV_POWER_STATUS_SERVO_VALID:
            status += 'S'
        if m.flags & mavutil.mavlink.MAV_POWER_STATUS_PERIPH_OVERCURRENT:
            status += 'O1'
        if m.flags & mavutil.mavlink.MAV_POWER_STATUS_PERIPH_HIPOWER_OVERCURRENT:
            status += 'O2'
        Data.power_status = status
        Data.Vcc = m.Vcc * 0.001  # 5V rail voltage in millivolts
        Data.Vservo = m.Vservo * 0.001

    # Stores various radio status in Data
    def handle_radio(self, m):
        if m.rssi < m.noise + 10 or m.remrssi < m.remnoise + 10:
            status = 'RED'
        else:
            status = 'BLACK'
        Data.radio_status["color"] = status
        Data.radio_status["rssi"] = m.rssi
        Data.radio_status["noise"] = m.noise
        Data.radio_status["remrssi"] = m.remrssi
        Data.radio_status["remnoise"] = m.remnoise

    # updates the altitude and airspeed error in Data
    def handle_nav_controller(self, m):
        Data.alt_error = m.alt_error
        Data.airspeed_error = m.aspd_error * 0.01

    # updates the current waypoint in data
    def handle_current_wp(self, m):
        Data.currentWPIndex = m.seq

    # updates the waypoints in Data and copies the SDA status
    def update_waypoints(self):
        wploader = self.mpstate.public_modules['wp'].wploader
        if wploader.wpoints != Data.wplist and (hasattr(wploader, 'expected_count') and len(wploader.wpoints) == wploader.expected_count):
            logger.info('waypoint change!')
            Data.wplist = list(wploader.wpoints)

    # updates the current flight mode in Data
    def update_flight_mode(self):
        Data.pdata['FLIGHT_MODE'] = self.master.flightmode

    # updates the status of Armed in Data
    def update_armed(self):
        if not (self.master.motors_armed() == Data.armed):
            Data.armed = self.master.motors_armed()
            logger.info('arm changed!')

    # updates the status of the safety switch in Data
    def update_livesafe(self):
        if 'SYS_STATUS' in self.mpstate.status.msgs:
            Data.safe = self.mpstate.status.msgs['SYS_STATUS'].onboard_control_sensors_enabled & mavutil.mavlink.MAV_SYS_STATUS_SENSOR_MOTOR_OUTPUTS

    def mavlink_packet(self, m):
        '''handle an incoming mavlink packet from the master vehicle.
        Relay it to the tracker if it is a GLOBAL_POSITION_INT'''
        logging.debug(str(datetime.now()) + " Type: " + str(m.get_type()))
        logging.debug(str(datetime.now()) + " Message: " + str(m))

        mt = m.get_type()  # message type
        if mt == 'PARAM_VALUE' and not self.mpstate.airapi:
            self.handle_param(m)
        elif mt == 'HEARTBEAT':
            self.handle_heartbeat(m)
        elif mt == 'GPS_RAW_INT':
            self.handle_raw_gps(m)
        elif mt == 'VFR_HUD':
            self.handle_vfr_hud(m)
        elif mt == 'STATUSTEXT':
            self.handle_status_text(m)
        elif mt == 'SYS_STATUS':
            self.handle_sys_status(m)
        elif mt == 'EKF_STATUS_REPORT':
            self.handle_ekf(m)
        elif mt == 'HWSTATUS':
            self.handle_hw_status(m)
        elif mt == 'POWER_STATUS':
            self.handle_power_status(m)
        elif mt in['RADIO', 'RADIO_STATUS']:
            self.handle_radio(m)
        elif mt == 'NAV_CONTROLLER_OUTPUT':
            self.handle_nav_controller(m)
        elif mt in ['MISSION_CURRENT', "WAYPOINT_CURRENT"]:
            self.handle_current_wp(m)

        # Store all the most recent data
        Data.pdata[mt] = m

        Data.pdata['MOTORS_ARMED'] = self.mpstate.status.armed
        Data.pdata['LINK'] = (not self.master.linkerror)
        Data.pdata['HEARTBEAT'] = time.time()

        if not self.mpstate.airapi:
            self.update_waypoints()
        self.update_flight_mode()
        self.update_armed()
        self.update_livesafe()
        # self.update_powerboard_status()


def init(mpstate):
    global instance
    instance = WebServerModule(mpstate)
    return instance
