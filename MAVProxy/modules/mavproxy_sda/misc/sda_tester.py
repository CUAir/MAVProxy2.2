
from MAVProxy.modules.server.data import Data
from MAVProxy.modules.mavproxy_sda import SDAModule
from MAVProxy.modules.sda_geometry import *
from MAVProxy.mavproxy import MPState
from collections import deque
from gen_obstacles import create_random_test
from random import randrange
from MAVProxy.pymavlink import mavwp
import threading
import time
import sys
import utm
from flask import Flask
import json
import numpy as np
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
#                                   Classes                                 #
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

class MAVPacket:
    def __init__(self, lat, lon, alt):
        self.lat = lat 
        self.lon = lon 
        self.alt = alt
        self.relative_alt = alt

    def get_type(self):
        return 'GLOBAL_POSITION_INT'

'''class Waypoint:
    def __init__(self, x, y, z, sda=False):
        self.x = x
        self.y = y
        self.z = z
        self.sda = sda
    def __str__(self):
        return 'Waypoint (' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')'''

class Convert:
    class __Convert:
        def __init__(self):
            self.zone_number = None
            self.zone_letter = None
            
        def ll2m(self, lat, lon):
            easting, northing, zone_number, zone_letter = utm.from_latlon(lat, lon)
            self.zone_number = zone_number
            self.zone_letter = zone_letter
            return {'x': easting, 'y': northing}

        def m2ll(self, x, y):
            lat, lon = utm.to_latlon(x, y, self.zone_number, self.zone_letter)
            return {'lat': lat, 'lon': lon}

    instance = None

    def __init__(self):
        if not Convert.instance:
            Convert.instance = Convert.__Convert()

    def __getattr__(self, name):
        return getattr(self.instance, name)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
#                                   Test Case                               #
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#Testcase 3 is the testing suite - user created or randomly generated test cases
testcase = 3

if testcase == 0:
    stationary_obstacles = [] #[{'latitude': 42.45161301493975, 
                             #"longitude": -76.48231029510498,
                             #"cylinder_height": 100,
                             #"cylinder_radius": 50}]

    start_position = {'lat': 42.4506765, 'lon': -76.4852143, 'alt': 100}

    plane_position = {'lat': start_position['lat'], 'lon': start_position['lon'], 'alt': start_position['alt']}

    plane_velocity = 20  # m/s

    waypoints = [Waypoint(start_position['lat'], start_position['lon'], start_position['alt']),
                 Waypoint(42.4479271, -76.4850965, 100)] 

elif testcase == 1:
    stationary_obstacles = [{'latitude': 42.4491771, 
                             "longitude": -76.485113,
                             "cylinder_height": 400,
                             "cylinder_radius": 50}]

    start_position = {'lat': 42.4506765, 'lon': -76.4852143, 'alt': 100}

    plane_position = {'lat': start_position['lat'], 'lon': start_position['lon'], 'alt': start_position['alt']}

    plane_velocity = 20  # m/s

    waypoints = [Waypoint(start_position['lat'], start_position['lon'], start_position['alt']), 
                 Waypoint(42.4479271, -76.4850965, 100)]
    tempwaypoints = []

elif testcase == 2:

    stationary_obstacles = [] #[{'latitude': 42.45161301493975, 
                             #"longitude": -76.48231029510498,
                             #"cylinder_height": 100,
                             #"cylinder_radius": 50}]

    start_position = {'lat': 42.4506765, 'lon': -76.4852143, 'alt': 100}

    plane_position = {'lat': start_position['lat'], 'lon': start_position['lon'], 'alt': start_position['alt']}

    plane_velocity = 20  # m/s

    waypoints = [Waypoint(start_position['lat'], start_position['lon'], start_position['alt']),
                 Waypoint(42.4479271, -76.4850965, 100)] 

elif testcase == 3:
    if len(sys.argv) > 1:
       random_data = create_random_test(seed=sys.argv[1])
    else:
       random_data = create_random_test()
    stationary_obstacles = random_data[1]
    waypoints = [Waypoint(*coords) for coords in random_data[2]]
    plane_velocity = 50
    plane_position = random_data[3]
    start_position = plane_position

elif testcase == 4:

    stationary_obstacles = [] #[{'latitude': 42.45161301493975, 
                             #"longitude": -76.48231029510498,
                             #"cylinder_height": 100,
                             #"cylinder_radius": 50}]

    start_position = {'lat': 42.4506765, 'lon': -76.4852143, 'alt': 100}

    plane_position = {'lat': start_position['lat'], 'lon': start_position['lon'], 'alt': start_position['alt']}

    plane_velocity = 20  # m/s
    waypoints = [Waypoint(start_position['lat'], start_position['lon'], start_position['alt']), 
                 Waypoint(42.4479271, -76.4850965, 100)] 

elif testcase == 5:

    stationary_obstacles = [{'latitude': 42.4491771, 
                             "longitude": -76.485113,
                             "cylinder_height": 400,
                             "cylinder_radius": 50},
                             {'latitude': 42.4491771, 
                             "longitude": -76.484113,
                             "cylinder_height": 400,
                             "cylinder_radius": 50},
                             {'latitude': 42.4491771, 
                             "longitude": -76.486113,
                             "cylinder_height": 400,
                             "cylinder_radius": 50},
                             {'latitude': 42.4491771, 
                             "longitude": -76.487113,
                             "cylinder_height": 400,
                             "cylinder_radius": 50}]

    start_position = {'lat': 42.4506765, 'lon': -76.4852143, 'alt': 100}

    plane_position = {'lat': start_position['lat'], 'lon': start_position['lon'], 'alt': start_position['alt']}

    plane_velocity = 20  # m/s
    waypoints = [Waypoint(start_position['lat'], start_position['lon'], start_position['alt']), 
                 Waypoint(42.4479271, -76.4850965, 100)]
    tempwaypoints = []

elif testcase == 6:

    stationary_obstacles = [] #[{'latitude': 42.45161301493975, 
                             #"longitude": -76.48231029510498,
                             #"cylinder_height": 100,
                             #"cylinder_radius": 50}]

    start_position = {'lat': 42.4506765, 'lon': -76.4852143, 'alt': 100}

    plane_position = {'lat': start_position['lat'], 'lon': start_position['lon'], 'alt': start_position['alt']}

    plane_velocity = 20  # m/s

    waypoints = [Waypoint(start_position['lat'], start_position['lon'], start_position['alt']), 
                 Waypoint(42.4479271, -76.4850965, 100)] 

else:
    raise Exception("No test case: " + str(testcase) + "!")




##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
#                                   Server                                  #
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

app = Flask(__name__, static_url_path='')

@app.route("/")
def root_route():
    return 'root'

@app.route("/map")
def map_route():
    try:
        return app.send_static_file('maps.html')
    except Exception as e:
        # print str(e)
        return 'no'


@app.route("/stationary_obstacles")
def stationary_obstacles_route():
    return json.dumps(stationary_obstacles)

@app.route("/plane_position")
def plane_position_route():
    return json.dumps(plane_position)

@app.route("/waypoints")
def waypoints_route():
    lst = []
    for i, w in enumerate(waypoints):
        lst.append({"id": i, "lat": w.x, "lon": w.y, "alt": w.z})
    return json.dumps(lst)

@app.route("/tempwaypoints")
def temp_waypoints_route():
    lst = []
    try:
        for i, w in enumerate(tempwaypoints):
            lst.append({"id": i, "lat": w.x, "lon": w.y, "alt": w.z})
        return json.dumps(lst)
    except Exception as e:
        print str(e)

sdamod = None
use_fences = False
@app.route('/fences')
def fences_route():
    try:
        if not use_fences:
            return json.dumps([])
        else:
            if sdamod is None:
                print 'no sdamod'
                return json.dumps([])
            lst = []
            for wp in sdamod.fenceloader:
                lst.append({'lat': wp.x, 'lon': wp.y, 'alt': 0, 'sda': wp.sda})
            return json.dumps([lst])
    except Exception as e:
        print "error in fence_route", str(e)


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
#                                      Go                                   #
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
fence_full = [Waypoint(42.45724912857, -76.4934682846, 0), Waypoint(42.44467799943, -76.4929533004, 0), Waypoint(42.4443613137, -76.4683628082, 0), Waypoint(42.4569958309, -76.4685773849, 0)]
fence_small = [Waypoint(42.457373, -76.493846, 0), Waypoint(42.44402, -76.493846, 0), Waypoint(42.457373, -76.467804, 0), Waypoint(42.457373, -76.467804, 0)]

def setup():

    packet = {'stationary_obstacles': stationary_obstacles}
    Data.pdata['obstacles'] = packet

    # Add a waypoint 
    Data.currentWPIndex = 1
    Data.waypoints = waypoints
    
    for w in waypoints:
        Data.wplist.append(w)

    # Add initial position
    packet = MAVPacket(start_position['lat'], start_position['lon'], start_position['alt'])
    Data.pdata['GLOBAL_POSITION_INT'] = packet

    # Create GeoFence
    fenceloader = mavwp.MAVFenceLoader()
    for p in fence_full:
        fenceloader.add(p)
    m = MPState(sdatester=True)

planexyz = np.array([0, 0, 0])
wpxyz = np.array([0, 0, 0])

def simulateMAVPackets(mod, run_event, speed):
    assert speed != 0, "Cannot simulate at zero speed!"

    while run_event.is_set():
        global waypoints
        waypoints = Data.wplist

        global tempwaypoints
        tempwaypoints = Data.twp 

        wp = Data.wplist[Data.currentWPIndex]

        # check if we have reached a waypoint 
        lat = abs(wp.x - Data.pdata['GLOBAL_POSITION_INT'].lat)
        lon = abs(wp.y - Data.pdata['GLOBAL_POSITION_INT'].lon)
        alt = abs(wp.z - Data.pdata['GLOBAL_POSITION_INT'].alt)

        if lat < 0.0001 and lon < 0.0001 and alt < 20:
            if Data.currentWPIndex < len(Data.wplist) - 1:
                Data.currentWPIndex += 1
            else:
                time.sleep(1/speed)
                sys.exit(0)

        # We're not at a waypoint; proceed.
        
        xy = Convert().ll2m(wp.x, wp.y)
        wpxyz = np.array([xy['x'], xy['y'], wp.z])

        xy = Convert().ll2m(Data.pdata['GLOBAL_POSITION_INT'].lat, Data.pdata['GLOBAL_POSITION_INT'].lon)
        planexyz = np.array([xy['x'], xy['y'], Data.pdata['GLOBAL_POSITION_INT'].alt])

        # direction vector
        dv = wpxyz - planexyz 
        mag = np.linalg.norm(dv)

        velocity_vector = dv/mag * plane_velocity / speed

        x = velocity_vector[0] + planexyz[0]
        y = velocity_vector[1] + planexyz[1]
        z = velocity_vector[2] + planexyz[2]

        planexyz = x, y, z
        latlon = Convert().m2ll(x, y)

        packet = MAVPacket(latlon['lat'], latlon['lon'], z)
        Data.pdata['GLOBAL_POSITION_INT'] = packet
        global plane_position
        plane_position = {'lat': latlon['lat'], 'lon': latlon['lon'], 'alt': z}
        mod.mavlink_packet(packet)

        time.sleep(1.0/speed)


def simulateObstacles(run_event, speed):
    while run_event.is_set():

        old_data = Data.pdata['obstacles']
        time.sleep(1.0/speed)


def run():
    setup()
    run_event = threading.Event()
    run_event.set()
    mod = SDAModule(MPState(sdatester=True), in_testing_mode=True)
    mod.enable_sda()
    global sdamod
    sdamod = mod
    simPacketsThread = threading.Thread(target=simulateMAVPackets, args=(mod, run_event, 10))
    simPacketsThread.start()
    obstacleThread = threading.Thread(target=simulateObstacles, args=(run_event, 10))
    obstacleThread.start()
    app.run()               # port = 5000
    run_event.clear()
    simPacketsThread.join()
    obstacleThread.join()

if __name__ == '__main__':
    run()