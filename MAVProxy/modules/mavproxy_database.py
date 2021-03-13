#!/usr/bin/env python

# Database module
# Creates database to access historical data
# October 2016

from modules.mavproxy_interop import interop
import mavproxy_logging
from modules.lib import mp_module

import sys
import os
import json
import time
import numpy as np
from collections import namedtuple
from datetime import datetime
import traceback

import subprocess

import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

from modules.lib import mp_module
from modules.server.helperFunctions import heading_to_vector, degrees_to_rads

logger = mavproxy_logging.create_logger("database")

TIME_VARIANCE = 5
TIME_VARIANCE_MAX = 10
TIME_HISTORY_MAX = 6000
HEARTBEAT_TIMEOUT = 3
# Number of seconds inconsistency between autopilot time and
# computer to at which to throw an error
TIME_INCONSISTENCY_MAX = 20
TIME_EPSILON_SECONDS = 1

class DatabaseModule(mp_module.MPModule):
    def __init__(self, mpstate):
        super(DatabaseModule, self).__init__(mpstate, "database", "database module", public=True)

        while True:
            try:
                self.pool = MySQLConnectionPool(pool_name="mavproxy_pool", pool_size=30, host=os.environ.get("DATABASE_HOST", "localhost"), user="cuair", passwd="aeolus", db="mavproxy", auth_plugin='mysql_native_password')
                break
            except mysql.connector.Error as e:
                logger.error("Cannot connect to MYSql database. Please start MYSql ('mysql.server start') or run setup_db.sh if MYSql has not been installed: " + str(e))
                logger.info("Retrying connection in 10 seconds...")
            
            time.sleep(10)

        self.autopilot_boot_time = None
        self.time_inconsistent = False

        if not mpstate.airapi:
            self.interop_instance = interop.get_instance()
            self.interop_instance.bind_to_new_obstacle(self.handle_interop_obstacles)

        self.Heartbeat = namedtuple('Heartbeat', ['time', 'plane_link'])
        self.heartbeat = self.Heartbeat(0, False)

        self.GPS_INT = namedtuple('GlobalPositionInt', ['time', 'rel_alt', 'asl_alt', 'lat', 'lon', 'heading', 'groundvx', 'groundvy', 'groundvz'])
        self.global_position_int = self.GPS_INT(0, 0, 0, 0, 0, 0, 0, 0, 0)

        self.GPS_STATUS = namedtuple('GPSStatus', ['time', 'satellite_number'])
        self.GPSStatus = self.GPS_STATUS(0, 0)

        self.VFR_HUD = namedtuple('VFRHUD', ['time', 'airvx', 'airvy', 'airvz', 'speed', 'climb', 'throttle'])
        self.vfr_hud = self.VFR_HUD(0, 0, 0, 0, 0, 0, 0)

        self.FLIGHT_TIME = namedtuple("FlightTime", ['time', 'time_start', 'is_flying'])
        self.flight_time = self.FLIGHT_TIME(0, None, False)

        self.WIND = namedtuple('Wind', ['time', 'windvx', 'windvy', 'windvz'])
        self.wind = self.WIND(0, 0, 0, 0)

        self.ATTITUDE = namedtuple("Attitude", ['time', 'roll', 'pitch', 'yaw', 'rollspeed', 'pitchspeed', 'yawspeed'])
        self.attitude = self.ATTITUDE(0, 0, 0, 0, 0, 0, 0)

        self.BATTERY = namedtuple("Battery", ['time', 'batterypct', 'batteryvoltage', 'batterycurrent'])
        self.battery = self.BATTERY(0, 0, 0, 0)

        self.MAV_INFO = namedtuple("MAVInfo", ['time', 'text', 'severity'])
        self.mav_info = self.MAV_INFO(0, "", 0)

        self.MAV_WARNING = namedtuple("MAVWarning", ['time', 'text', 'severity'])
        self.mav_warning = self.MAV_WARNING(0, "", 0)

        self.MAV_ERROR = namedtuple("MAVError", ['time', 'text', 'severity'])
        self.mav_error = self.MAV_ERROR(0, "", 0)

        self.CAMERA_FEEDBACK = namedtuple("CameraFeedback", ['ds_time', 'lat', 'lon', 'alt_rel', 'roll', 'pitch', 'yaw', 'mavproxy_time'])

        self.mode = "MAV"
        self.mode2num = {"UNKNOWN": -1, "MAV": -1, "MANUAL": 0, "CIRCLE": 1, "STABILIZE": 2, "TRAINING": 3, "ACRO": 4, "FBWA": 5, "FBWB": 6, "CRUISE": 7, "AUTOTUNE": 8, "AUTO": 10, "TL": 11, "LOITER": 12, "AVOID_ADSB": 14, "GUIDED": 15, "QSTABILIZE": 17, "QHOVER": 18, "QLOITER": 19, "QLAND": 20, "RTL" : 21, "INITIALISING" : 22}
        self.num2mode = {n: mode for mode, n in self.mode2num.items()}
        self.num2mode[-1] = "MAV"

        self.SIGNAL = namedtuple("Signal", ['time', 'signal_strength'])
        self.signal = self.SIGNAL(0, 0)

        self.STATIONARY_OBSTACLE = namedtuple("STATIONARY_OBSTACLES", ['time', 'lat', 'lon', 'cylinder_radius', 'cylinder_height'])
    
        self.WAYPOINT = namedtuple("WAYPOINT", ['command', 'current', 'param1', 'param2', 'param3', 'param4', 'lat', 'lon', 'alt', 'index'])
        self.wps = []  # these are mavwaypoints. use get_wps to get a list of WAYPOINT objects 

        self.current_waypoint_index = 0

    def _get_packet_time(self, msg):

        # # If the packet includes a time since boot, use autopilot boot time
        # # Better to ask forgiveness than permission
        # try:
        #     t = msg.time_boot_ms/1000.0 + self.autopilot_boot_time

        #     if not self.set_time and self.mpstate.airapi:
        #         self.set_time = True
        #         time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
        #         logger.info("Syncing system time to Autopilot time ({})".format(time_string))
        #         subprocess.call("(sudo /usr/local/bin/set-time.sh \"" + time_string + "\")", shell=True)

        #     if abs(t - time.time()) > TIME_INCONSISTENCY_MAX:
        #         if not self.time_inconsistent:
        #             self.time_inconsistent = True
        #             print("Autopilot time and computer system time are inconsistent")

        # except (AttributeError, TypeError):
        #     # Note that this also catches the case where we haven't set self.autopilot_boot_time yet
        #     # The most likely reason for this is that the GPS isn't working - we still want to store the packet though
        #     # So we resort to returning the current system time
        #    t = time.time()
        t = time.time()

        return datetime.fromtimestamp(t)

    def _db_connector(func):

        def wrapper(self, arg=None):
            try:
                conn = self.pool.get_connection()
                cursor = conn.cursor(buffered=True)  # set so we can fetchone when we don't want all the results
                r_value = None
                try:
                    r_value = func(self, cursor, arg)

                except mysql.connector.IntegrityError as e:
                    pass
                except mysql.connector.Error as e:
                    logger.error("MYSQl error in " + str(func) + ": " + str(e))
                conn.commit()
                conn.close()
                return r_value
            except Exception as e:
                logger.error(traceback.format_exc())

        return wrapper

    # @param data: [ [t1, t1_data1, t1_data2, t1_data3], [t2, t2_data1, t2_data2, t2_data3], [t3, t3_data1, t3_data2, t3_data3] ]
    # @param goal_time: time to interopolate to in seconds.
    # @returns [tgoal_data1, tgoal_data2, tgoal_data3]
    def interpolate(self, data, req_time):
        if len(data) < 1 or len(data[0]) < 1:
            logger.debug("Empty data, cannot interpolate")
            return data
        data = data[:10]  # don't use tons of old data
        interpolated = [req_time]
        times = [d[0].strftime("%s") for d in data]  # get the unix time version of each datetime
        for i in range(1, len(data[0])):
            values = [d[i] for d in data]
            interpolated.append(np.interp(req_time, times, values))
        return interpolated

    # Gets data close by a to a particular time with linear backoff for interpolation
    def get_nearby_data(self, cursor, req_time, query, fetch_one=False):
        modifier = 0
        closest = []
        while not closest and (TIME_VARIANCE+modifier) < TIME_VARIANCE_MAX:
            # print modifier
            time_start = req_time - TIME_VARIANCE - modifier
            time_end = req_time + TIME_VARIANCE + modifier
            cursor.execute(query, (time_start, time_end, req_time))
            if not fetch_one:
                closest = cursor.fetchall()
            else:
                closest = cursor.fetchone()
            modifier += 1
        return closest

    def make_interpolated_query(self, cursor, req_time, query):
        closest = self.get_nearby_data(cursor, req_time, query)
        return self.interpolate(closest, req_time)


    # returns a list of waypoints as a dict
    def mavwp_to_wps(self, wplist):
        def wp2dict(wp):
            return self.WAYPOINT(wp.command, wp.current, float(wp.param1), float(wp.param2), float(wp.param3), float(wp.param4), float(wp.x), float(wp.y), float(wp.z), wp.seq)._asdict()

        return map(wp2dict, wplist)

    def get_wps(self):
        return self.mavwp_to_wps(self.wps)

    # ###################
    #
    #
    #    HANDLES (POSTS)
    #
    #
    # ###################

    @_db_connector
    def handle_waypoints(self, cursor, arg):
        wploader = self.mpstate.public_modules['wp'].wploader

        # Update if our waypoints are out of date, and the loader is at the expected count.
        if wploader.wpoints != self.wps and len(wploader.wpoints) == wploader.expected_count:
            # If the waypoints change, then the minimum distance to each waypoint calculated before
            # is no longer valid, so reset it.
            

            self.wps = list(wploader.wpoints)

            data = (datetime.now(), json.dumps(self.mavwp_to_wps(self.wps)))
            query = """
                    INSERT INTO
                      waypoints (time, json)
                    VALUES
                      (%s, %s);
                    """

            if not self.mpstate.airapi:
                self.mpstate.public_modules['mission'].reset_min_dists()
            cursor.execute(query, data)

    @_db_connector
    def handle_mode(self, cursor, arg):
        if self.mode != self.master.flightmode:
            # mode has changed
            
            # These next two lines are pretty janky and someone should trace it 
            # back to see why the error occurs in the first place
            if self.master.flightmode.startswith("Mode"):
                self.master.flightmode = self.num2mode[int(self.master.flightmode[5:-1])]
            self.mode = self.master.flightmode
            data = (datetime.now(), self.mode2num[self.mode])
            query = """
                    INSERT INTO
                      mode (time, mode)
                    VALUES
                      (%s, %s);
                    """
            if not self.mpstate.airapi:
                cursor.execute(query, data)

    @_db_connector
    def handle_heartbeat(self, cursor, msg):
        # Note: We're only callling this function after we've received a heartbeat from the plane
        # so there will never be a linkerror when this function is called. The boolean stored is
        # never referenced but is left in to avoid needing to update the database schema
        self.heartbeat = self.Heartbeat(self._get_packet_time(msg),
                                        not self.master.linkerror)

        query = """
                INSERT INTO plane_link
                  (time, plane_link)
                VALUES
                  (%s, %s);
                """
        if not self.mpstate.airapi:
            cursor.execute(query, self.heartbeat)

    @_db_connector
    def handle_global_position_int(self, cursor, msg):
        self.global_position_int = self.GPS_INT(self._get_packet_time(msg),                  # seconds
                                                float(msg.relative_alt) / 1000,    # meters
                                                float(msg.alt) / 1000,             # meters
                                                float(msg.lat) / pow(10, 7),       # decimal
                                                float(msg.lon) / pow(10, 7),       # decimal
                                                msg.hdg / float(100),              # degrees
                                                msg.vx / float(100),               # m/s
                                                msg.vy / float(100),               # m/s
                                                msg.vz / float(100))               # m/s
        query = """
                INSERT INTO global_position_int
                  (time, rel_alt, asl_alt, lat, lon, heading, groundvx, groundvy, groundvz)
                VALUES
                  (%s,%s,%s,%s,%s,%s,%s,%s,%s);
                """
        if not self.mpstate.airapi:
            cursor.execute(query, self.global_position_int)

    @_db_connector
    def handle_vfr_hud(self, cursor, msg):
        airx, airy = heading_to_vector(msg.heading, msg.airspeed)
        airz = self.global_position_int.groundvz
        self.vfr_hud = self.VFR_HUD(self._get_packet_time(msg),        # seconds
                                    airx,                  # m/s
                                    airy,                  # m/s
                                    airz,                  # m/s
                                    msg.airspeed,            # m/s
                                    msg.climb,               # m/s
                                    float(msg.throttle))     # pct
        query = """
                INSERT INTO
                  vfr_hud (time, airspeedvx, airspeedvy, airspeedvz, speed, climb, throttle)
                VALUES
                  (%s,%s,%s,%s,%s,%s,%s);
                """
        if not self.mpstate.airapi:
            cursor.execute(query, self.vfr_hud)

    @_db_connector
    def handle_flight_time(self, cursor, msg):
        # if the throttle is on and it is climbing and this is the first time this has been seen then 
        # this is the start of the flight time
        if(msg.throttle > 2 and msg.climb > 2 and not self.flight_time.is_flying):
            self.flight_time = self.FLIGHT_TIME(self._get_packet_time(msg), self._get_packet_time(msg), True)
        # if the flight has started and you are still moving then the plane is still in flight
        elif(msg.airspeed > 2 and self.global_position_int.rel_alt > 2 and self.flight_time.is_flying):
            self.flight_time = self.FLIGHT_TIME(self._get_packet_time(msg), self.flight_time.time_start, True)
        else:
            self.flight_time = self.FLIGHT_TIME(self._get_packet_time(msg), self.flight_time.time_start, False)

        query = """
                INSERT INTO
                  flight_time (time, time_start, is_flying)
                VALUES
                  (%s, %s, %s);
                """
        if not self.mpstate.airapi:
            cursor.execute(query, self.flight_time)

    @_db_connector
    def handle_signal(self, cursor, msg):
        self.signal = self.SIGNAL(self._get_packet_time(msg), msg.rssi)
        query = """
                INSERT INTO signal_status
                  (time, signal_strength)
                VALUES
                  (%s, %s);
                """

        if not self.mpstate.airapi:
            cursor.execute(query, self.signal)

    @_db_connector
    def handle_attitude(self, cursor, msg):
        self.attitude = self.ATTITUDE(self._get_packet_time(msg),         # seconds
                                      msg.roll,                 # rad -pi...+pi
                                      msg.pitch,                # rad -pi...+pi
                                      msg.yaw,                  # rad -pi...+pi
                                      msg.rollspeed,            # rad/s
                                      msg.pitchspeed,           # rad/s
                                      msg.yawspeed)             # rad/s

        query = """
                INSERT INTO attitude
                  (time, roll, pitch, yaw, rollspeed, pitchspeed, yawspeed)
                VALUES
                  (%s,%s,%s,%s,%s,%s,%s);
                """
        if not self.mpstate.airapi:
            cursor.execute(query, self.attitude)

    @_db_connector
    def handle_status_text(self, cursor, msg):
        if '#EP' in msg.text and len(self.wps) > 0:
            lat, lon = msg.text.split('#EP:')[1].split(',')
            self.wps[0].x = float(lat)
            self.wps[0].y = float(lon)

        data = (self._get_packet_time(msg),
                msg.text,
                msg.severity)            # 0: emergency, 1: alert, 2: critical, 3: error, 4: warning, 5: notice, 6: info

        if msg.severity == 6:
            self.mav_info = self.MAV_INFO(*data)
        elif msg.severity in (5, 4):
            self.mav_warning = self.MAV_WARNING(*data)
        elif msg.severity < 4:
            self.mav_error = self.MAV_ERROR(*data)

        query = """
                INSERT INTO mav_message
                  (time, text, severity)
                VALUES
                  (%s, %s, %s)
                """
        if not self.mpstate.airapi:
            cursor.execute(query, data)

    @_db_connector
    def handle_sys_status(self, cursor, msg):
        self.battery = self.BATTERY(self._get_packet_time(msg),                      # seconds
                                    float(msg.battery_remaining),          # percent
                                    float(msg.voltage_battery) / 1000.0, # Volts
                                    float(msg.current_battery) / 10.0)  # mAh

        query = """
                INSERT INTO battery
                  (time, batterypct, batteryvoltage, batterycurrent)
                VALUES
                  (%s, %s, %s, %s)
                """
        if not self.mpstate.airapi:
            cursor.execute(query, self.battery)

    @_db_connector
    def handle_wind(self, cursor, msg):
        windx, windy = heading_to_vector(msg.direction, msg.speed)
        self.wind = self.WIND(self._get_packet_time(msg),        # seconds
                              windx,                  # m/s
                              windy,                  # m/s
                              msg.speed_z)              # m/s

        query = """
                INSERT INTO wind
                  (time, windx, windy, windz)
                VALUES
                  (%s, %s, %s, %s);
                """

        if not self.mpstate.airapi:
            cursor.execute(query, self.wind)

    @_db_connector
    def handle_current_wp(self, cursor, msg):
        self.current_waypoint_index = msg.seq

        data = (self._get_packet_time(msg),  # datetime
                msg.seq)           # int

        query = """
                INSERT INTO current_wp
                  (time, current_wp)
                VALUES
                  (%s, %s);
                """

        if not self.mpstate.airapi:
            cursor.execute(query, data)

    @_db_connector
    def handle_gps_status(self, cursor, msg):
        self.GPSStatus = self.GPS_STATUS(self._get_packet_time(msg),
                                         msg.satellites_visible)
        query = """
                INSERT INTO gps_status
                  (time, satellite_number)
                VALUES
                  (%s, %s);
                """

        if not self.mpstate.airapi:
            cursor.execute(query, self.GPSStatus)


    def handle_ekf(self, msg):
        pass

    def handle_hw_status(self, msg):
        pass

    def handle_power_status(self, msg):
        pass

    def handle_radio(self, msg):
        pass

    def handle_nav_controller(self, msg):
        pass

    def handle_param(self, msg):
        pass

    # @param obstacles: {'stationary_obstaces': {"lat": lat, "lon": lon, "cylinder_radius": cylinder_radius, "cylinder_height": cylinder_height} }
    # @param t: option time in seconds
    @_db_connector
    def handle_interop_obstacles(self, cursor, obstacles):
        if 'stationary_obstacles' not in obstacles:
            logger.error("handle_interop_obstacles: incorrect obstacle format: {}".format(obstacles.keys()))
            return
        data = (datetime.now(),
                json.dumps(obstacles['stationary_obstacles']))

        query = """
                INSERT INTO obstacles
                  (time, st_obstacles)
                VALUES
                  (%s, %s);
                """

        if not self.mpstate.airapi:
            cursor.execute(query, data)

    @_db_connector
    def handle_camera_feedback(self, cursor, msg):
        data = (msg.time_usec, float(msg.lat) / pow(10, 7), 
                float(msg.lng) / pow(10, 7), msg.alt_rel,
                degrees_to_rads(msg.roll),     # Comes from roll_sensor in degrees 0-360, converting to -pi...+pi
                degrees_to_rads(msg.pitch),    # Comes from pitch_sensor in degrees 0-360, converting to -pi...+pi
                degrees_to_rads(msg.yaw),      # Comes from yaw_sensor in degrees 0-360, converting to -pi...+pi
                datetime.fromtimestamp(time.time()), msg.img_idx)
        query = """
                INSERT INTO camera_feedback
                  (ds_time, lat, lon, alt_rel,
                   roll, pitch, yaw,
                   mavproxy_time, image_index)
                VALUES
                  (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        cursor.execute(query, data)

    # #############
    #
    #
    #    GETS
    #
    #
    # #############
    @_db_connector
    def get_camera_feedback(self, cursor, req_time=None):
        if req_time is None:
            return None
        query = """
                SELECT
                  ds_time
                  , lat
                  , lon
                  , alt_rel
                  , roll
                  , pitch
                  , yaw
                  , mavproxy_time
                FROM 
                  camera_feedback
                WHERE
                  ds_time = %s
                """
        cursor.execute(query, (req_time,))
        data = cursor.fetchone()
        try:
            cam_feedback = self.CAMERA_FEEDBACK(*data)._asdict()
            cam_feedback['mavproxy_time'] = cam_feedback['mavproxy_time'].strftime('%s')
            return cam_feedback
        except TypeError as e:
            logger.error("get_camera_feedback:" + str(e) + str(data))
        return None       


    @_db_connector
    def get_attitude(self, cursor, req_time=None):
        if req_time is None:
            return self.attitude._asdict()
        elif not self.mpstate.airapi:
            query = """
                    SELECT
                      time
                      , roll
                      , pitch
                      , yaw
                      , rollspeed
                      , pitchspeed
                      , yawspeed
                    FROM attitude
                    WHERE time > FROM_UNIXTIME(%s) AND time < FROM_UNIXTIME(%s)
                    ORDER BY ABS(DATEDIFF(time, FROM_UNIXTIME(%s)))
                    """
            data = self.make_interpolated_query(cursor, req_time, query)
            if len(data) == 0:
                logger.debug("get_attitude: no data at time {}".format(req_time))
                return None
            try:
                return self.ATTITUDE(*data)._asdict()
            except TypeError as e:
                logger.error("get_attitude:" + str(e) + str(data))
                return None
        else:
            raise ValueError("Database query not supported in AirAPI mode")

    @_db_connector
    def get_param(self, cursor, req_time=None):
        pass

    @_db_connector
    def get_heartbeat(self, cursor, req_time=None):
        if req_time is None:
            data = abs(self.heartbeat[0] - time.time()) < HEARTBEAT_TIMEOUT
        elif not self.mpstate.airapi:
            query = """
                    SELECT
                      time
                    FROM plane_link
                    WHERE time > FROM_UNIXTIME(%s) and time < FROM_UNIXTIME(%s)
                    ORDER BY ABS(DATEDIFF(time, FROM_UNIXTIME(%s)))
                    """

            time_start = req_time - TIME_VARIANCE
            time_end = req_time
            cursor.execute(query, (time_start, time_end, req_time))

            closest = cursor.fetchall()
            if len(closest) == 0:
                data = False
            else:
                data = abs(time.mktime(closest[-1][0].timetuple()) - req_time) < HEARTBEAT_TIMEOUT
        else:
            raise ValueError("Database query not supported in AirAPI mode")

        return data

    @_db_connector
    def get_gps_status(self, cursor, req_time=None):
        if req_time is None:
            return self.GPSStatus._asdict()
        elif not self.mpstate.airapi:
            query = """
                    SELECT
                        time
                      , satellite_number
                    FROM gps_status
                    WHERE time > FROM_UNIXTIME(%s) and time < FROM_UNIXTIME(%s)
                    ORDER BY ABS(DATEDIFF(time, FROM_UNIXTIME(%s)))
                    """
            time_start = req_time - TIME_VARIANCE
            time_end = req_time + TIME_VARIANCE
            cursor.execute(query, (time_start, time_end, req_time))

            closest = cursor.fetchone()
            if closest is None:
                logger.debug("get_gps_status: no data at time {}".format(req_time))
                return 0
            else:
                return self.GPS_STATUS(*closest)._asdict()
        else:
            raise ValueError("Database query not supported in AirAPI mode")

    @_db_connector
    def get_flight_time(self, cursor, req_time=None):
        if req_time is None:
            return self.flight_time._asdict()
        elif not self.mpstate.airapi:
            query = """
                    SELECT
                        time
                      , time_start
                      , is_flying
                    FROM flight_time
                    WHERE time > FROM_UNIXTIME(%s) and time < FROM_UNIXTIME(%s)
                    ORDER BY ABS(DATEDIFF(time, FROM_UNIXTIME(%s)))
                    """

            cursor.execute(query, (req_time - TIME_VARIANCE, req_time + TIME_VARIANCE, req_time))

            closest = cursor.fetchone()
            if closest is None:
                logger.debug("get_flight_time: no data at time {}".format(req_time))
                return 0
            else:
                # as it turns out mysql does not store booleans as true or false it stores them as 0 and 1 
                # this was causing the closest tupple to have an int for the value that represented is_flying (a bool)
                # this changes the 0s and 1s back to booleans
                lst = list(closest)
                lst[2] = bool(lst[2])
                toReturn = tuple(lst)

                return self.FLIGHT_TIME(*toReturn)._asdict()
        else:
            raise ValueError("Database query not supported in AirAPI mode")

    @_db_connector
    def get_gps(self, cursor, req_time=None):
        if req_time is None:
            return self.global_position_int._asdict()
        elif not self.mpstate.airapi:
            query = """
                    SELECT
                        time
                      , rel_alt
                      , asl_alt
                      , lat
                      , lon
                      , heading
                      , groundvx
                      , groundvy
                      , groundvz
                    FROM global_position_int
                    WHERE time > FROM_UNIXTIME(%s) AND time < FROM_UNIXTIME(%s)
                    ORDER BY ABS(DATEDIFF(time, FROM_UNIXTIME(%s)))
                    """
            data = self.make_interpolated_query(cursor, req_time, query)
            if len(data) == 0:
                logger.debug("get_gps: no data at time {}".format(req_time))
                return None
            try:
                return self.GPS_INT(*data)._asdict()
            except TypeError as e:
                logger.error("get_gps: " + str(e))
                return None
        else:
            raise ValueError("Database query not supported in AirAPI mode")

    # @param time: time in seconds
    # @returns dict of format VFR_HUD or None if unavailable
    @_db_connector
    def get_vfr_hud(self, cursor, req_time=None):
        if req_time is None:
            return self.vfr_hud._asdict()
        elif not self.mpstate.airapi:
            query = """
                    SELECT
                        time
                      , airspeedvx
                      , airspeedvy
                      , airspeedvz
                      , speed
                      , climb
                      , throttle
                    FROM vfr_hud
                    WHERE time > FROM_UNIXTIME(%s) AND time < FROM_UNIXTIME(%s)
                    ORDER BY ABS(DATEDIFF(time, FROM_UNIXTIME(%s)))
                    """
            data = self.make_interpolated_query(cursor, req_time, query)

            if len(data) == 0:
                logger.debug("get_vfr_hud: no data at time {}".format(req_time))
                return None

            try:
                return self.VFR_HUD(*data)._asdict()
            except TypeError as e:
                logger.error("get_vfr_hud" + str(e))
                return None
        else:
            raise ValueError("Database query not supported in AirAPI mode")

    @_db_connector
    def get_signal(self, cursor, req_time=None):
        if req_time is None:
            return self.signal._asdict()
        elif not self.mpstate.airapi:
            query = """
                    SELECT
                        time
                      , signal_strength
                    FROM signal_status
                    WHERE time > FROM_UNIXTIME(%s) and time < FROM_UNIXTIME(%s)
                    ORDER BY ABS(DATEDIFF(time, FROM_UNIXTIME(%s)))
                    """
            cursor.execute(query, (req_time - TIME_VARIANCE, req_time + TIME_VARIANCE, req_time))

            closest = cursor.fetchone()
            if closest is None:
                logger.debug("get_signal : no data at time {}".format(req_time))
                return None
            else:
                return self.SIGNAL(*closest)._asdict()
        else:
            raise ValueError("Database query not supported in AirAPI mode")

    @_db_connector
    def get_status_text(self, cursor, req_time=None):
        if req_time is None:
            return {'info_text': self.mav_info.text, 'warning_text': self.mav_warning.text, 'error_text': self.mav_error.text}
        elif not self.mpstate.airapi:
            # 0: emergency, 1: alert, 2: critical, 3: error, 4: warning, 5: notice, 6: info
            query = """
                    SELECT
                        COALESCE(CASE WHEN severity = 6 THEN text END) as info
                      , COALESCE(CASE WHEN severity >= 4 AND severity <= 5 THEN text END) as warning
                      , COALESCE(CASE WHEN severity < 4 THEN text END) as error
                    FROM mav_message
                    WHERE time < FROM_UNIXTIME(%s)
                    AND   time > FROM_UNIXTIME(%s)
                    ORDER BY time desc
                    """

            cursor.execute(query, (req_time, req_time - TIME_HISTORY_MAX))
            data = cursor.fetchone()
            if data is None or len(data) < 3:
                logger.debug("get_status_text: bad data {} is null.".format(data))
                return

            return {'info_text': data[0], 'warning_text': data[1], 'error_text': data[2]}
        else:
            raise ValueError("Database query not supported in AirAPI mode")

    @_db_connector
    def get_sys_status(self, cursor, req_time=None):
        if req_time is None:
            return self.battery._asdict()
        elif not self.mpstate.airapi:
            query = """
                    SELECT
                        time
                      , batterypct      # percent
                      , batteryvoltage  # volts
                      , batterycurrent  # current
                    FROM battery
                    WHERE time > FROM_UNIXTIME(%s) AND time < FROM_UNIXTIME(%s)
                    ORDER BY ABS(DATEDIFF(time, FROM_UNIXTIME(%s)))
                    """
            data = self.make_interpolated_query(cursor, req_time, query)

            if len(data) == 0:
                logger.debug("get_sys_status: no data at time {}".format(req_time))
                return None

            try:
                return self.BATTERY(*data)._asdict()
            except TypeError as e:
                logger.error("get_sys_status" + str(e))
                return None
        else:
            raise ValueError("Database query not supported in AirAPI mode")

    @_db_connector
    def get_wind(self, cursor, req_time=None):
        if req_time is None:
            return self.wind._asdict()
        elif not self.mpstate.airapi:
            query = """
                    SELECT
                        time
                      , windx
                      , windy
                      , windz
                    FROM wind
                    WHERE time > FROM_UNIXTIME(%s) AND time < FROM_UNIXTIME(%s)
                    ORDER BY ABS(DATEDIFF(time, FROM_UNIXTIME(%s)))
                    """
            data = self.make_interpolated_query(cursor, req_time, query)

            if len(data) == 0:
                logger.debug("get_wind: no data at time {}".format(req_time))
                return None
        else:
            raise ValueError("Database query not supported in AirAPI mode")

        try:
            return self.WIND(*data)._asdict()
        except TypeError as e:
            logger.error("get_wind error" + str(e))
            return None

    @_db_connector
    def get_waypoints(self, cursor, req_time=None):
        if req_time is not None and self.mpstate.airapi:
            raise ValueError("Database query not supported in AirAPI mode")
        try:
            if req_time is None:
                return self.mavwp_to_wps(self.wps)
            else:
                query = """
                        SELECT
                          json
                        FROM waypoints
                        WHERE time < FROM_UNIXTIME(%s)
                        AND   time > FROM_UNIXTIME(%s)
                        ORDER BY time desc;
                        """
                cursor.execute(query, (req_time, req_time - TIME_HISTORY_MAX))
                result = cursor.fetchone()
                if result is None:
                    logger.debug('get_waypoints: no data at time {}'.format(req_time))
                    return []
                return json.loads(result[0])
        except Exception as e:
            logger.error("get_waypoints error {}".format(str(e)))

    @_db_connector
    def get_mode(self, cursor, req_time=None):
        if req_time is None:
            return self.master.flightmode
        elif not self.mpstate.airapi:
            query = """
                    SELECT
                      mode
                    FROM mode
                    WHERE time < FROM_UNIXTIME(%s)
                    AND   time > FROM_UNIXTIME(%s)
                    ORDER by time desc;
                    """
            cursor.execute(query, (req_time, req_time - TIME_HISTORY_MAX))
            result = cursor.fetchone()  # returns tuple of length one (0, )
            if result is None:
                return "MAV"
            return self.num2mode[result[0]]
        else:
            raise ValueError("Database query not supported in AirAPI mode")

    @_db_connector
    def get_interop_obstacles(self, cursor, req_time=None):
        if req_time is None:
            return self.interop_instance.obstacles
        elif not self.mpstate.airapi:
            query = """
                    SELECT
                        time
                      , st_obstacles
                    FROM obstacles
                    WHERE time < FROM_UNIXTIME(%s)
                    AND   time > FROM_UNIXTIME(%s)
                    ORDER BY time desc;
                    """
            cursor.execute(query, (req_time, req_time - TIME_HISTORY_MAX))
            result = cursor.fetchone()

            if result is None:
                return []

            mv_obstacles = json.loads(result[1])
            st_obstacles = json.loads(result[2])
        else:
            raise ValueError("Database query not supported in AirAPI mode")
        return {'time': result[0], 'stationary_obstacles': st_obstacles}

    @_db_connector
    def get_ekf(self, cursor, req_time=None):
        raise NotImplementedError

    @_db_connector
    def get_hw_status(self, cursor, req_time=None):
        raise NotImplementedError

    @_db_connector
    def get_power_status(self, cursor, req_time=None):
        raise NotImplementedError

    @_db_connector
    def get_radio(self, cursor, req_time=None):
        raise NotImplementedError

    @_db_connector
    def get_nav_controller(self, cursor, req_time=None):
        raise NotImplementedError

    @_db_connector
    def get_current_wp(self, cursor, req_time=None):
        if req_time is None:
            data = self.current_waypoint_index
        elif not self.mpstate.airapi:
            query = """
                    SELECT
                      current_wp
                    FROM current_wp
                    WHERE time < FROM_UNIXTIME(%s)
                    AND   time > FROM_UNIXTIME(%s)
                    ORDER BY time desc
                    LIMIT 1;
                    """
            cursor.execute(query, (req_time, req_time - TIME_HISTORY_MAX))
            data_tuple = cursor.fetchone()
            
            if data_tuple is None:
                raise ValueError("No data for time: " + str(req_time))
            data = data_tuple[0]
        else:
            raise ValueError("Database query not supported in AirAPI mode")

        return data

    def mavlink_packet(self, msg):
        try:   # use giant try catch so mavproxy doesn't eat this errors
            msgt = msg.get_type()  # message type

            if msgt == 'SYSTEM_TIME' and msg.time_unix_usec != 0:
                if self.autopilot_boot_time is None:
                    self.autopilot_boot_time = (msg.time_unix_usec/1000.0 - msg.time_boot_ms)/1000.0
                    new_time = round(msg.time_unix_usec / 1000000)
                    logger.info("Recorded autopilot boot time: " + str(datetime.fromtimestamp(new_time)))
                    if self.mpstate.airapi:
                        time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(new_time))
                        logger.info("Syncing system time to Autopilot time ({})".format(time_string))
                        subprocess.call("(sudo /usr/local/bin/set-time.sh \"" + time_string + "\")", shell=True)

            if msgt == 'PARAM_VALUE':
                self.handle_param(msg)
            elif msgt == 'HEARTBEAT':
                self.handle_heartbeat(msg)
            elif msgt == 'GLOBAL_POSITION_INT':
                self.handle_global_position_int(msg)
            elif msgt == 'ATTITUDE':
                self.handle_attitude(msg)
            elif msgt == 'VFR_HUD':
                self.handle_vfr_hud(msg)
                self.handle_flight_time(msg)
            elif msgt == 'WIND':
                self.handle_wind(msg)
            elif msgt == 'STATUSTEXT':
                self.handle_status_text(msg)
            elif msgt == 'SYS_STATUS':
                self.handle_sys_status(msg)
            elif msgt == 'EKF_STATUS_REPORT':
                self.handle_ekf(msg)
            elif msgt == 'HWSTATUS':
                self.handle_hw_status(msg)
            elif msgt == 'POWER_STATUS':
                self.handle_power_status(msg)
            elif msgt in['RADIO', 'RADIO_STATUS']:
                self.handle_radio(msg)
            elif msgt in['RC_CHANNELS', 'RC_CHANNELS_RAW']:
                self.handle_signal(msg)
            elif msgt == 'NAV_CONTROLLER_OUTPUT':
                self.handle_nav_controller(msg)
            elif msgt == 'GPS_RAW_INT':
                self.handle_gps_status(msg)
            elif msgt in ['MISSION_CURRENT', "WAYPOINT_CURRENT"]:
                self.handle_current_wp(msg)
            elif msgt == 'CAMERA_FEEDBACK':
                self.handle_camera_feedback(msg)
                
            self.handle_waypoints(None)
            self.handle_mode(None)

        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logger.error("mavlink_packet: " + str(e) + str(exc_type) + str(fname) + str(exc_tb.tb_lineno))


instance = None
def get_db_mod():
    global instance
    if (instance is None):
        raise Exception("DatabaseModule Not Initialized")
    return instance


def init(mpstate):
    global instance
    instance = DatabaseModule(mpstate)
    return instance
