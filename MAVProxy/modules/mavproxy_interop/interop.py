#!/usr/bin/env python
import requests
# import thread
import threading
import time
import os
import json
from modules.mavproxy_interop import interop_api_pb2
from google.protobuf import json_format

from collections import deque
from geopy.distance import geodesic as gps_distance

from modules.lib import mp_module

instance = None

FEET_TO_METERS_FACTOR = 3.2808399
TRIES_BEFORE_FAILURE = 3
WAYPOINT_THRESHOLD_DISTANCE_FEET = 50
MOVING_AVERAGE_SIZE = 30
POST_ATTEMPT_MAX = 1
POST_TIMEOUT_SECONDS = 2
GET_UPDATE_RATE = .1

# CUAir is using custom logging rather than printing this year
# If it doesn't find the CUAir logger it'll just use a generic one
# that essentially acts the same as a print statement
try:
    import mavproxy_logging
    logger = mavproxy_logging.create_logger("interop")
except:
    import logging
    logger = logging.getLogger("interop")
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

print("interop1")
class Interop(mp_module.MPModule):
    def __init__(self, mpstate):
        super(Interop, self).__init__(mpstate, "interop", "AUVSI interoperability module")
        self.add_command('interop_obst', self._print_obstacles, "show interop obstacle data")
        self.add_command('interop_start', self.start, "start sending and receiving interop data")
        self.add_command('interop_stop', self.stop, "stop sending and receiving interop data")
        self.add_command('interop_hz', self._print_post_hz, "show interop post frequency moving average")
        self.add_command('interop_wp', self._print_waypoint_min_dists, "show minimum distance from each waypoint")
        self.add_command('interop', self._print_help, "shows a help message for using the interop command line")

        self.is_active = False
        self.get_working = True
        self.consecutive_post_failures = 0

        self.session = None
        # Used for cookies
        self.login_response = None
        self.interop_url = None

        self.last_post_time = 0
        # Queue to be used for a rolling average of frequency
        self.post_hz_list = []

        self.mission_waypoints = []

        self.obstacles = None
        #self.obstacle_history = None

        self.mission = None
        self.mission_id = 1
        # List of closest points of approach to each waypoint, in feet
        self.min_wp_dists = []

        # list of functions to run on new obstacles
        self.binders = []

    def get_active_mission_from_server(self):
        mission = self.session.get(self.interop_url + "/api/missions/" + str(self.mission_id), cookies=self.login_response.cookies)
        mission = json.loads(mission.text)

        # Check for active mission - if found, update the instance variable
        # If not, set the instance variable to None
        # Done this way to ensure there is no moment at which the self.active_missions variable
        # is in an incorrect state when it doesn't have to be
        self.mission = mission
            # Ensure that the mission waypoints always match the ones given by the server
            # If we lose the active mission, we keep the old mission waypoints
        self.setup_waypoints()
        self.setup_obstacles()
        # break
        # else: # Only runs if the loop exited normally, not through 'break'
        #     if self.active_mission:
        #         logger.error("No active mission exists")
        #     self.active_mission = None

    def setup_obstacles(self):
        metric_obstacles = {"stationary_obstacles" : []}
        obstacles = self.mission['stationaryObstacles']
        for obst in obstacles:
            metric_obstacles["stationary_obstacles"].append({'latitude': obst["latitude"],
                                "longitude": obst["longitude"],
                                "height": feet_to_meters(obst["height"]),
                                "radius": feet_to_meters(obst["radius"])})
        self.obstacles = metric_obstacles
        for f in self.binders:
            try:
                f(self.obstacles)
            except Exception as e:
                logger.error("get_interop_data Error from: " + str(f) + " Message: " + str(e))

    def get_main_loop(self):
        start = time.time()
        while(self.is_active):
            # Sleep until it's time to get data again, or just continue if it's
            # already time
            time.sleep(max(GET_UPDATE_RATE - (time.time() - start),0))

            try:
                self.get_active_mission_from_server()
                if not self.get_working:
                    logger.info("GET working again")
                    self.get_working = True
            except Exception as ex:
                if self.get_working:
                    self.get_working = False
                    logger.error("EXCEPTION while 'GETing': " + str(ex))

            start += GET_UPDATE_RATE

    def send_telemetry_post_request(self, telemetry_data):
        for _ in range(POST_ATTEMPT_MAX):
            try:
                
                telemetry_data_string = json.dumps(telemetry_data)
                telem_response = self.session.post(self.interop_url + "/api/telemetry",
                                                    cookies=self.login_response.cookies,
                                                    data=telemetry_data_string,
                                                    timeout=POST_TIMEOUT_SECONDS)
                telem_response.raise_for_status()
                self.update_wp_dists(telemetry_data)
                if self.last_post_time:
                    self.post_hz_list.append(time.time() - self.last_post_time)

                # List must be at max the proper size, so we take an item
                # off the beginning of a queue to maintain the rolling average
                if len(self.post_hz_list) > MOVING_AVERAGE_SIZE:
                    self.post_hz_list = self.post_hz_list[1:]

                if self.consecutive_post_failures > 0:
                    self.consecutive_post_failures = 0
                    logger.info("POST working again")
                self.last_post_time = time.time()

                return True
            except Exception as e:
                # Move on, try again if the loop hasn't finished yet
                pass

        if self.consecutive_post_failures == 0:
            logger.error("BAD RESPONSE TO SENT TELEMETRY DATA: " + str(e))
        self.consecutive_post_failures += 1

        if self.consecutive_post_failures == TRIES_BEFORE_FAILURE:
            logger.error("-------------------------------------------------------")
            logger.error("ERROR INTEROP MODULE IS FAILING TO POST TELEMETRY DATA")
            logger.error("-------------------------------------------------------")

    # Sets up the waypoint objects to be used for alert when each waypoint has been reached
    def setup_waypoints(self):
        if self.using_file:
            filepath = os.path.split(os.path.realpath(__file__))[0]
            with open(filepath + "/waypoints.json", "r") as waypoint_file:
                json_string = waypoint_file.read()
                # convert to json
                # Expect the string to be formatted as valid JSON as follows
                # Altitude is MEAN SEA LEVEL (absolute altitude) in FEET
                # [{"altitude_msl":0, "latitude":0, "longitude":0},{"altitude_msl":0, "latitude":0, "longitude":0},.....]
                unicode_wp_json = json.loads(json_string)
                # convert out of unicode encoding
                for wp in range(len(unicode_wp_json)):
                    self.mission_waypoints.append({"altitude": unicode_wp_json[wp][u'altitude'],
                                               "latitude": unicode_wp_json[wp][u'latitude'],
                                               "longitude": unicode_wp_json[wp][u'longitude']})

        else:
            # Interop server spec makes no guarantee they're listed in order, so we'll sort them based
            # on the order given
            self.mission_waypoints = self.mission['waypoints']
        # Important note: We only track whether the mission length changed, no action will be taken if
        # the waypoints change without adding or removing waypoints.
        if not self.min_wp_dists or len(self.min_wp_dists) != len(self.mission_waypoints):
            if self.min_wp_dists:
                logger.warning("Active mission changed length. Resetting minimum distance from each waypoint")
            self.min_wp_dists = [None] * len(self.mission_waypoints)

    # Uses the exact telemetry data posted to interop to print to terminal when a waypoint has been reached
    def update_wp_dists(self, telem_data):
        if self.mission_waypoints:
            for x in range(len(self.mission_waypoints)):
                plane_gps_coords = (telem_data['latitude'], telem_data['longitude'])
                wp_gps_coords = (self.mission_waypoints[x]['latitude'], self.mission_waypoints[x]['longitude'])

                xy_dist = gps_distance(plane_gps_coords, wp_gps_coords).feet
                z_dist = abs(telem_data['altitude'] - self.mission_waypoints[x]['altitude'])
                total_dist = (z_dist**2 + xy_dist**2)**.5

                if self.min_wp_dists[x]:
                    if total_dist < self.min_wp_dists[x]:
                        if total_dist < WAYPOINT_THRESHOLD_DISTANCE_FEET and self.min_wp_dists[x] >= WAYPOINT_THRESHOLD_DISTANCE_FEET:
                            logger.info("##############################################\n\n")
                            logger.info("          WAYPOINT " + str(x) + " REACHED\n\n")
                            logger.info("##############################################")
                        self.min_wp_dists[x] = total_dist
                else:
                    self.min_wp_dists[x] = total_dist

    # Overrides the parent class's mavlink_packet function, will be called
    # every time a new packet arrives
    def mavlink_packet(self, m):
        if self.is_active and m.get_type() == "GLOBAL_POSITION_INT":
            telemetry_data = {
                                'latitude': to_standard_gps_coord(m.lat),
                                'longitude': to_standard_gps_coord(m.lon),
                                'altitude': meters_to_feet(millimeters_to_meters(m.alt)),
                                'heading': centidegrees_to_degrees(m.hdg),
                              }
            thread.start_new_thread(self.send_telemetry_post_request,(telemetry_data,))


    ##################
    # Public methods #
    ##################
    def bind_to_new_obstacle(self, function):
        self.binders.append(function)

    def get_obstacles(self):
        return self.obstacles if self.obstacles else {"stationary_obstacles":[]}

    def get_obstacle_history(self):
        return self.obstacle_history 
        
    def get_wp_min_dists(self):
        return self.min_wp_dists

    def get_rolling_frequency(self):
        return len(self.post_hz_list) / sum(self.post_hz_list) if self.post_hz_list else -1

    def is_working(self):
        return self.get_working or self.consecutive_post_failures > 0

    def server_active(self):
        return self.is_active

    def get_login_file(self):
        return os.path.split(os.path.realpath(__file__))[0] + "/login_data.json"

    def get_active_mission(self):
        return self.mission

    def get_mission_waypoints(self):
        return self.mission_waypoints

    # Starts sending data to and receiving data from the judge's interop server
    # returns True if it successfully logs in and initializes, otherwise false
    def start(self, args):
        self.obstacle_history = ()

        try:
            filepath = os.path.split(os.path.realpath(__file__))[0]
            with open(filepath + "/login_data.json", "r") as login_file:
                json_string = login_file.read()
                # convert to json
                # Expect the string to be formatted as valid JSON as follows
                # Altitude is MEAN SEA LEVEL (absolute altitude) in FEET
                # [{"altitude_msl":0, "latitude":0, "longitude":0},{"altitude_msl":0, "latitude":0, "longitude":0},.....]
                unicode_login_data = json.loads(json_string)

                username = unicode_login_data[u'username']
                password = unicode_login_data[u'password']
                self.interop_url = unicode_login_data[u'server_url']
                self.mission_id = unicode_login_data[u'mission_id']
        except Exception as e:
            logger.error("failed to read login_data.json file")
            logger.error(str(e))
            return False

        self.using_file = args and args['0'].lower() == "file"

        try:
            # Login
            creds = interop_api_pb2.Credentials()
            creds.username = username
            creds.password = password
            payload = json_format.MessageToJson(creds)
            self.login_response = requests.post(self.interop_url + "/api/login", data=payload, timeout=5)
            self.session = requests.Session()
            # Get the missions
            self.get_active_mission_from_server()
        except Exception as e:
            logger.error(e)
            return False

        logger.info("Interop server started")
        self.is_active = True

        thread.start_new_thread(self.get_main_loop,())

        return True

    def stop(self, args):
        if self.is_active:
            logger.info("Interop server stopped")
            self.is_active = False
            self.consecutive_post_failures = 0
            self.get_working = True
            self.post_hz_list = []
        else:
            logger.error("Interop not active")

    def _print_obstacles(self, args):
        if self.obstacles:
            logger.info("Stationary Obstacles: ")
            logger.info("----------------------")
            for obs in range(len(self.obstacles["stationaryObstacles"])):
                logger.info("Obstacle " + str(obs) + ":")
                for key in self.obstacles["stationaryObstacles"][obs]:
                    logger.info(key + ": " + str(self.obstacles["stationaryObstacles"][obs][key]))
                print ("\n")
        else:
            logger.info("No obstacle data")

    def _print_post_hz(self, args):
        if self.post_hz_list:
            logger.info("Rolling POST frequency: " + str((len(self.post_hz_list) / sum(self.post_hz_list))) + " hz")
        else:
            logger.info("No data")

    def _print_waypoint_min_dists(self, args):
        if self.min_wp_dists:
            for d in range(len(self.min_wp_dists)):
                if self.min_wp_dists[d]:
                    logger.info("Waypoint " + str(d) + ": " + str(int(self.min_wp_dists[d])) + " feet")
                else:
                    logger.info("No data for waypoint " + str(d))
        else:
            logger.info("No waypoints")

    def _print_help(self, args):
        logger.info('usage: ["interop_start | interop_stop | interop_hz | interop_wp | interop"]')

    def unload(self):
        if self.is_active:
            logger.warning("Stopping interop server")
        self.stop(True)


def meters_to_feet(meters):
    return meters * FEET_TO_METERS_FACTOR


def feet_to_meters(feet):
    return feet / FEET_TO_METERS_FACTOR


def to_standard_gps_coord(coord):
    return coord / float(pow(10, 7))


def millimeters_to_meters(dist):
    return dist / 1000.0


def centidegrees_to_degrees(deg):
    return deg / 100.0


def get_instance():
    if instance is None:
        raise Exception("Interop instance not yet initialized")
    return instance


def init(mpstate):
    '''initialize module'''
    global instance
    instance = Interop(mpstate)
    return instance
