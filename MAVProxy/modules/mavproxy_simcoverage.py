from modules.lib import mp_module
from modules.mavproxy_sda.sda_util import Convert
from modules.lib.mp_geometry import Segment, Point, Convert
from modules.mavproxy_database import get_db_mod
from modules.mavproxy_wp import get_wp_mod
from modules.lib import mp_module
from LatLon23 import LatLon

from modules.mavproxy_coverage.coverage_engine import get_coverage_mod
import mavproxy_logging
import modules.lib.mp_geometry as mp_geo
import sys
import os
import json
import shapely.geometry as sg
import numpy as np
import math

logger = mavproxy_logging.create_logger("simcoverage")

class SimCoverageModule(mp_module.MPModule):
    
    def __init__(self, mpstate):
        super(SimCoverageModule, self).__init__(mpstate, "simcoverage", "sim coverage module", public=True)

    def simulate(self, camlag=2.7, hor_fov=76, ver_fov=50.6):
        logger.info("Starting Sim Coverage")
        plane_speed = self.mpstate.public_modules["param"].get_mav_param("TRIM_ARSPD_CM")/100.0
        self.waypoints = get_db_mod().get_waypoints()
        self.converter = Convert(self.waypoints[0]['lat'], self.waypoints[0]['lon'])
        coverage_boxes = []
        for i in range(len(self.waypoints)-1):
            x1, y1 = self.converter.ll2m(self.waypoints[i]['lat'], self.waypoints[i]['lon'])
            x2, y2 = self.converter.ll2m(self.waypoints[i+1]['lat'], self.waypoints[i+1]['lon'])
            og_dist = self.calc_wpdist(x1, y1, x2, y2)
            curr_dist = og_dist

            
            while curr_dist > 0:
                dist_traveled = og_dist-curr_dist
                curr_height = ((self.waypoints[i+1]['alt'] - self.waypoints[i]['alt']) / (og_dist)) * (og_dist-curr_dist) + self.waypoints[i]['alt']
                curr_dist -= (plane_speed * camlag)
                coverage_poly = self.fov_box(self.calc_planepos(x1, y1, x2, y2, dist_traveled, og_dist), curr_height, (np.arctan2(y2-y1, x2-x1)+np.pi/2), self.converter, roll_limit=[hor_fov/2.0, -hor_fov/2.0], pitch_limit=[ver_fov/2.0, -ver_fov/2.0])
                coverage_boxes.append(coverage_poly)

        get_coverage_mod().picture_add_coverage_all(coverage_boxes)
    def calc_wpdist(self, x1, y1, x2, y2):
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return dist

    def calc_planepos(self, x1, y1, x2, y2, dist_traveled, og_dist):
        vector = np.asarray([x2-x1, y2-y1])
        r_0 = np.asarray([x1, y1])
        r = r_0 + dist_traveled/og_dist*vector
        return r

    def fov_box(self, plane_pos, plane_alt, plane_yaw, converter, roll_limit=[90,-90], pitch_limit=[70,-45],max_roll=70,max_pitch=70):
        # Calculating possible gimbal angles
        roll_limit = np.asarray(roll_limit) 
        pitch_limit = np.asarray(pitch_limit)

        max_angles = np.radians(np.array(np.meshgrid(roll_limit, pitch_limit)).T.reshape(-1,2))
        max_angles[[-2,-1]] = max_angles[[-1,-2]]

        # Getting the coverage points
        pos = np.tan(max_angles) * plane_alt

        # Get the rotation matrix based on yaw
        c, s = np.cos(plane_yaw), np.sin(plane_yaw)
        R = np.array([[c, -s], [s, c]])

        # Rotate the coverage and center it on the plane position
        rotated_pos = []
        for i in range(len(pos)):
            rotated_pos.append(R.dot(pos[i].T).T)
        rotated_pos = np.asarray(rotated_pos) + np.asarray(plane_pos)

        # If needed to debug use coverage module to show image_data
        im_data = []
        for i in range(len(rotated_pos)):
            im_data.append(converter.m2ll(rotated_pos[i][0], rotated_pos[i][1]))

        image_data = {
            'topRight':{"lat": im_data[0]['lat'], "lon": im_data[0]['lon']},
            'topLeft' : {"lat": im_data[1]['lat'], "lon": im_data[1]['lon']}, 
            'bottomLeft':{"lat": im_data[2]['lat'], "lon": im_data[2]['lon']}, 
            'bottomRight':{"lat": im_data[3]['lat'], "lon": im_data[3]['lon']}, 
        }
        return image_data
        

instance = None
def get_simcoverage_mod():
    global instance
    if (instance is None):
        raise Exception("SpotCoverageModule Not Initialized")
    return instance


def init(mpstate):
    '''initialize module'''
    global instance
    instance = SimCoverageModule(mpstate)
    return instance
