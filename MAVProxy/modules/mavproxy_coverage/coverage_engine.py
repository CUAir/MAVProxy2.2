from __future__ import division
from modules.lib import mp_module
from PIL import Image, ImageDraw
from geopy.distance import geodesic as gps_distance
import math
import os
import json
import time
import requests
from bisect import bisect

import mavproxy_logging

instance = None
logger = mavproxy_logging.create_logger("ground coverage")

IMAGE_SIZE = 2560
WRITE_INTERVAL_SECS = 3 # number of seconds between writes



class GroundCoverageModule(mp_module.MPModule):
    """
    Module calculates the ground coverage of the plane
    """
    def __init__(self, mpstate):
        super(GroundCoverageModule, self).__init__(mpstate, "coverage", "Ground Coverage")
        self.add_command('reset_coverage', self.reset_coverage, 'Resets the coverage image', [""])
        self.version = 0
        self.filepath = os.path.split(os.path.realpath(__file__))[0]
        self.image_filepath = os.path.join(self.filepath, "../server/static/img/coverage.png")
        self.reset_coverage()
        self.pixDimX = 0
        self.pixDimY = 0
        self.leftLon = 0
        self.rightLon = 0
        self.topLat = 0
        self.bottomLat = 0
        self.last_write = time.time();
        self.in_bounds = False
        self.manual_entry = False
        self.im = None

    def find_map(self, image_data):
        """
        Select most likely map
        If none is found, defaults to Competition and displays error
        """
        with open(self.filepath + "/../server/locations.json", "r") as location_file:
            json_string = location_file.read()
            location_info = json.loads(json_string)
            for map_info in location_info.values():
                for corner in ['topLeft', 'bottomLeft', 'bottomRight', 'topRight']:
                    curr = image_data[corner]
                    if (map_info["leftLon"] < curr['lon'] and curr['lon'] < map_info["rightLon"]) and \
                     (map_info["bottomLat"] < curr['lat'] and curr['lat'] < map_info["topLat"]):
                        self.leftLon = map_info["leftLon"]
                        self.rightLon = map_info["rightLon"]
                        self.topLat = map_info["topLat"]
                        self.bottomLat = map_info["bottomLat"]
                        self.in_bounds = True
                        self.pixel_dimension()
                        return self.in_bounds
            if self.in_bounds:
                logger.error("Coverage rectangle is outside all known map image bounds. ")
            map_info = location_info["Competition"]
            self.leftLon = map_info["leftLon"]
            self.rightLon = map_info["rightLon"]
            self.topLat = map_info["topLat"]
            self.bottomLat = map_info["bottomLat"]
            self.pixel_dimension()
            self.in_bounds = False
            return self.in_bounds

    def manual_config(self):
        """
        Sets map specified in coverage.json
        """
        self.coverage_config = os.path.join(self.filepath, "coverage.json")
        with open(self.coverage_config, "r") as coverage_file:
            json_string = coverage_file.read()
            self.coverage_info = json.loads(json_string)
        self.in_bounds = True
        self.manual_entry = False

    def latlon_to_pix(self, image_data):
        """
        Convert latitude and longitude to pixels
        """
        corner_data = []
        for corner in ['topLeft', 'bottomLeft', 'bottomRight', 'topRight']:
            curr = image_data[corner]
            if not (self.leftLon < curr['lon'] < self.rightLon) or not (self.bottomLat < curr['lat'] < self.topLat):
                if self.in_bounds:
                    self.in_bounds = False
                    self.manual_entry = True
                    logger.error("Coverage rectangle is outside map image bounds. " 
                                 "Try changing the image in " + self.coverage_config)
            else:
                self.in_bounds = True
        
            x = gps_distance((self.topLat, self.leftLon), (self.topLat, curr['lon'])).meters * self.pixDimX
            y = gps_distance(( self.topLat, self.leftLon), (curr['lat'], self.leftLon, )).meters * self.pixDimY
            corner_data.append((x, y))
        return corner_data

    def pixel_dimension(self):
        """
        Calculates the conversion between pixels and meters
        """
        oneSideMetersX = gps_distance((self.topLat, self.leftLon), (self.topLat, self.rightLon, )).meters
        self.pixDimX = IMAGE_SIZE / oneSideMetersX

        oneSideMetersY = gps_distance((self.topLat, self.leftLon), (self.bottomLat, self.leftLon)).meters
        self.pixDimY = IMAGE_SIZE / oneSideMetersY

    def reset_coverage(self, args=None):
        """
        Creates a new PNG overlay that covers the entirety of the map
        """
        filepath = os.path.split(os.path.realpath(__file__))[0]
        mask = Image.new('RGBA', (IMAGE_SIZE, IMAGE_SIZE))
        mask.save(filepath + "/../server/static/img/coverage.png", "PNG")
        self.im = None
        self.version += 1

    def picture_add_coverage(self, image_data, color="gray"):
        """
        Sets the upper left corner's x and y components
        """
        if not self.in_bounds and not self.manual_entry:
            self.find_map(image_data)
        elif not self.in_bounds:
            self.manual_config()
        vertices = self.latlon_to_pix(image_data)

        # only load coverage.png first time through
        if self.im is None:
            self.im = Image.open(self.image_filepath)

        draw = ImageDraw.Draw(self.im)
        draw.polygon(vertices, fill=color)

        now = time.time();
        if (now - self.last_write) > WRITE_INTERVAL_SECS:
            self.im.save(self.image_filepath)
            self.last_write = now

        self.version += 1

    def picture_add_coverage_all(self, image_data_list):
        """
        Sets the upper left corner's x and y components
        """
        if len(image_data_list) > 0:
            if not self.in_bounds and not self.manual_entry:
                self.find_map(image_data_list[0])
            elif not self.in_bounds:
                self.manual_config()

            # only load coverage.png first time through
            if self.im is None:
                self.im = Image.open(self.image_filepath)

            draw = ImageDraw.Draw(self.im)

            for image_data in image_data_list:
                vertices = self.latlon_to_pix(image_data)
                draw.polygon(vertices, fill="gray")

            now = time.time();
            if (now - self.last_write) > WRITE_INTERVAL_SECS:
                self.im.save(self.image_filepath)
                self.last_write = now

            self.version += 1

def get_coverage_mod():
    global instance
    if (instance is None):
        raise Exception("GroundCoverageModule Not Initialized")
    return instance


def init(mpstate):
    global instance
    instance = GroundCoverageModule(mpstate)
    return instance
