#!/usr/bin/env python
'''mission progress and planning management'''

from __future__ import division
import sys
import math
from modules.lib import mp_module
from geopy.distance import geodesic as gps_distance
from collections import namedtuple
from pymavlink.mavutil import mavlink
# from modules.mavproxy_sda import sda_util
import numpy

import mavproxy_logging

logger = mavproxy_logging.create_logger("mission")
LANDING_SEQ = 3  # nth to last waypoint, beginning of landing sequence
SPEED_SAMPLE_SIZE = 10  # average speed computed by last n waypoints
MAX_FLIGHT_TIME = 5000  # longest possible flight time in seconds
MIN_FLIGHT_SPEED = 5  # minimum speed in mps to be considered flying

BezierCurve = namedtuple("BezierCurve", ["start", "control1", "control2", "end"])

LOCATION_SCALING_FACTOR_INV = 89.83204953368922 * 1e-7
DEG_TO_RAD = math.pi / 180

SPLINE_CONTROLLER = 2


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def longitude_scale(lat, lon):
    scale = math.cos(lat * DEG_TO_RAD)
    return constrain(scale, 0.01, 1.0)


def location_offset(lat, lon, ofs_north, ofs_east):
    if ofs_north != 0 and ofs_east != 0:
        dlat = ofs_north * LOCATION_SCALING_FACTOR_INV
        dlon = ofs_east * LOCATION_SCALING_FACTOR_INV / longitude_scale(lat, lon)
        return lat + dlat, lon + dlon
    return lat, lon


def tuple2latlng(tup):
    return {'lat': tup[0]/1e7, 'lon': tup[1]/1e7}


def xy2mag(x, y):
    return math.sqrt(x ** 2 + y ** 2)


class MissionModule(mp_module.MPModule):
    def __init__(self, mpstate):
        super(MissionModule, self).__init__(mpstate, "mission", "mission info handling", public=True)
        self.db = self.mpstate.public_modules['database']
        self.prev_gps_loc = None
        self.last_waypoint = 0
        self.avg_speed = 0
        self.flight_progress = {}
        self.min_wp_dists = []
        self.spline_path = []

        self.add_command('mission', self.cmd_mission, 'mission info',
                         ["<ttl|covered|percent>"])
        self.add_command('clear_splines', self.clear_splines, 'clear existing spline path',
                         [""])

    def mavlink_packet(self, m):
        '''handle and incoming mavlink packets'''
        mtype = m.get_type()

        if mtype in ["WAYPOINT_CURRENT", "MISSION_CURRENT"]:
            if m.seq != self.last_waypoint:
                # called every time the current wp is incremented or updated
                self.last_waypoint = m.seq
                # @todo(#299) once flight time remaining is implemented, remove this
                if m.seq == len(self.db.wps) - LANDING_SEQ:
                    self.on_landing()
        elif mtype == "GLOBAL_POSITION_INT":
           self.handle_gps_packet(m)
        elif mtype == "SPLINE_CONTROL_POINTS":
            self.add_next_spline_segment(m)

    def cmd_mission(self, args):
        if len(args) != 1:
            logger.warning("usage: mission <ttl|covered|percent>")
            return
        if args[0] == "ttl":
            logger.info(str(self.flight_progress["time_to_landing"]) + " seconds to landing")
        if args[0] == "covered":
            logger.info(str(self.flight_progress["covered"]) + " meters covered")
        if args[0] == "percent":
            logger.info(str(self.flight_progress["percentage"]) + " percent of flight path flown")

    def on_landing(self):
        '''actions to occur on landing'''
        if "distributed" in self.mpstate.public_modules:
            self.mpstate.public_modules['distributed'].landing()
        else:
            logger.error("Distributed module not loaded: failed to notify of landing")

    def handle_gps_packet(self, gps_state):
        '''actions to occur on receipt of an updated GPS packet'''
        latitude = to_standard_gps_coord(gps_state.lat)
        longitude = to_standard_gps_coord(gps_state.lon)
        relative_alt = millimeters_to_meters(gps_state.relative_alt)
        plane_gps_coords = (latitude, longitude)

        # compute flight progress
        prog = self._get_wp_progress((plane_gps_coords, relative_alt))
        # scalar speed based on GPS velocities
        gps_speed = ((gps_state.vx/100)**2 + (gps_state.vy/100)**2 + (gps_state.vz/100)**2)**.5
        s = SPEED_SAMPLE_SIZE
        # calculate average speed over the past `s` samples
        self.avg_speed = self.avg_speed * (s/(s+1.0)) + gps_speed * (1.0/(s+1.0))
        time_left = 0
        # compute time left in flight by distance remaining vs average speed
        if self.avg_speed > 0 and gps_speed > MIN_FLIGHT_SPEED:
            # only need time_left when actually in flight, zero otherwise
            time_left = abs(prog["remaining"] / self.avg_speed)
        if time_left > MAX_FLIGHT_TIME:
            # this only happens during takeoff or very slow motion
            time_left = 0
        prog["time_to_landing"] = int(time_left)
        self.flight_progress = prog

        # calculate min distance to waypoints
        waypoints = self.db.wps
        if len(waypoints) != len(self.min_wp_dists):
            self.reset_min_dists()

        if self.prev_gps_loc is not None:
            for i, wp in enumerate(list(waypoints)):
                # wp_gps_coords = sda_util.Point(wp.x, wp.y)
                # plane_gps_arr = sda_util.Point(*plane_gps_coords)
                # prev_plane_gps_arr = sda_util.Point(*self.prev_gps_loc)
                # interp_segment = sda_util.Segment(plane_gps_arr, prev_plane_gps_arr)
                closest_point = interp_segment.projection(wp_gps_coords)

                if wp.command == mavlink.MAV_CMD_DO_JUMP:
                    total_dist = 0
                else:
                    closest_point = (closest_point.x, closest_point.y)
                    xy_dist = gps_distance(closest_point, (wp.x, wp.y)).meters
                    z_dist = abs(relative_alt - wp.z)
                    total_dist = (z_dist**2 + xy_dist**2)**.5

                if self.min_wp_dists[i] and total_dist < self.min_wp_dists[i]:
                    self.min_wp_dists[i] = total_dist
        self.prev_gps_loc = plane_gps_coords

    def _get_wp_progress(self, plane_loc):
        '''given (<plane coordinates>, <plane altitude>), returns progress along
           waypoint path as an object'''
        progress = {}
        just_passed_wp = self.last_waypoint - 1
        waypoints = self.db.wps
        if(len(waypoints) <= 2):
            # no waypoints so return no progress
            progress["covered"] = 0
            progress["remaining"] = 0
            progress["percentage"] = 0
            return progress
        total_dist = 0  # total length of the flight plan
        covered_dist = 0  # length of the flight plan that has been flown so far
        for i in range(len(waypoints) - 2):
            wp_num = i + 1  # ignore the home waypoint
            wp1 = waypoints[wp_num]  # earlier of the two waypoints being compared
            wp2 = waypoints[wp_num + 1]  # latter of the two waypoints
            wp1_gps_loc = ((wp1.x, wp1.y), wp1.z)
            wp2_gps_loc = ((wp2.x, wp2.y), wp2.z)
            res_dist = dist_between_locations(wp1_gps_loc, wp2_gps_loc)
            total_dist += res_dist
            # only add to covered dist if wp1 is before most recently passed wp
            if wp_num + 1 <= just_passed_wp:
                covered_dist += res_dist

        # add estimation of plane distance between prev and next waypoints
        if just_passed_wp + 1 <= len(waypoints):  # only if not at last wp
            passed_wp = waypoints[just_passed_wp]
            next_wp = waypoints[just_passed_wp + 1]
            passed_gps_loc = ((passed_wp.x, passed_wp.y), passed_wp.z)
            next_gps_loc = ((next_wp.x, next_wp.y), next_wp.z)
            # get dist between passed wp and plane, next wp and plane, and both wps
            passed_dist = dist_between_locations(passed_gps_loc, plane_loc)
            next_dist = dist_between_locations(next_gps_loc, plane_loc)
            wp_diff = dist_between_locations(passed_gps_loc, next_gps_loc)
            # map progress percent between wps on to dist between the two
            covered_dist += wp_diff * (passed_dist / (passed_dist + next_dist))

        flight_percent = min(100.0 * (covered_dist / total_dist), 100.0)
        # update the progress object
        progress["covered"] = int(covered_dist)
        progress["remaining"] = int(total_dist - covered_dist)
        progress["percentage"] = flight_percent
        return progress

    def add_next_spline_segment(self, m):
        db = self.mpstate.public_modules["database"]
        # Don't create spline for takeoff waypoint or landing waypoint
        if self.last_waypoint == 1 or self.last_waypoint >= len(db.get_wps()) - 1:
            return

        cps = [(m.cp1_lat, m.cp1_lon), (m.cp2_lat, m.cp2_lon), (m.cp3_lat, m.cp3_lon), (m.cp4_lat, m.cp4_lon)]

        self.spline_path.append(map(tuple2latlng, BezierCurve(*cps)))

    def clear_splines(self, args=None):
        logger.info("Cleared spline path")
        self.spline_path = []

    def get_progress(self):
        return self.flight_progress

    def get_min_dists(self):
        return self.min_wp_dists

    def reset_min_dists(self):
        self.min_wp_dists = [sys.maxint] * len(self.db.wps)


instance = None
def get_mission_mod():
    global instance
    if (instance is None):
        raise Exception("MissionModule Not Initialized")
    return instance


def init(mpstate):
    '''initialise module'''
    global instance
    instance = MissionModule(mpstate)
    return instance


def dist_between_locations(l1, l2):
    '''Given two locations structured as ((<lat>, <lon>), <alt>), computes 
       distance in meters between the two'''
    xy_dist = gps_distance(l1[0], l2[0]).meters
    z_dist = abs(l1[1] - l2[1])
    return (z_dist**2 + xy_dist**2)**.5

def to_standard_gps_coord(coord):
    return coord / float(pow(10, 7))


def millimeters_to_meters(dist):
    return dist / 1000.0


def centidegrees_to_degrees(deg):
    return deg / 100.0

def meters_to_feet(meters):
    return meters * FEET_TO_METERS_FACTOR
