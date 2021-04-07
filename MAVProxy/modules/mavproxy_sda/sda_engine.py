#!/usr/bin/env python
from modules.server.data import Data
from modules.lib import mp_module
from modules.lib import mp_util
from pymavlink import mavutil
from modules import mavproxy_wp
from modules import mavproxy_database
from modules.mavproxy_sda.sda_rrt import RRTree
from modules.mavproxy_sda.sda_path import Path
import modules.lib.mp_geometry as mp_geo
import modules.mavproxy_interop.interop as interop
import math
import time
import traceback
import os
import sys
import copy
import numpy as np
import modules.mavproxy_sda.sda_pdriver as sda_pdriver
import threading, multiprocessing 

from collections import deque
#if mp_util.has_wxpython:
#    from modules.lib.mp_menu import *
import mavproxy_logging

logger = mavproxy_logging.create_logger("sda engine")

# TODO: Write comments
class SDAModule(mp_module.MPModule):

    WAYPOINT_LOOKAHEAD_COUNT = 5
    MAX_PLANE_LOCATION_DATA_POINTS = 50
    FLIGHT_PATH_RECALCULATION_PERIOD = 1

    def __init__(self, mpstate):
        super(SDAModule, self).__init__(mpstate, "sda", "sda module", public=True) 
        self.mpstate = mpstate
        self.sda_on = False
        self.plane_gps_history = deque()
        self.convert = mp_geo.convert_instance
        self.base_alt = 0
        self.wplist = []
        self.is_loitering = False
        self.active_listener_thread = None
        self.current_process = None
        self.all_processes = []
        self.is_bound = False

        self.fully_autonomous = False

        self.last_run = time.perf_counter()

        self.estimated_speed = 16 # m/s

        # OUTDATED --------
        # TODO: Determine k max. 10 is not correct
        #self.path = Path(0.009)
        # END OUTDATED ----

        self.geofence = None
        #self.get_geofence()
         #TODO: Get geofences into SDA.
        self.pdriver = sda_pdriver.ProbDriver(model=sda_pdriver.ProbModelLinearInterp())
        #self.get_geofence()

        # increment = 5 meters
        # constrain = True
        # min_turning_radius = 40 meters
        # timeout = 2 seconds 
        self.rrt = RRTree(self.pdriver.current_model, self.geofence, increment=5, constrain=False, min_turning_radius=40, timeout=4)
        self.path_dict_manager = multiprocessing.Manager()
        self.path_dict = self.path_dict_manager.dict()
        self.rrt.speed = self.estimated_speed

    def mavlink_packet(self, m):
        '''handle an incoming mavlink packet'''
        if m.get_type() == 'GLOBAL_POSITION_INT':
            item = {'lat': float(m.lat),
                    'lon': float(m.lon),
                    'alt': float(m.alt)/ 1000,
                    'time': time.time()}
            self.base_alt = (float(m.alt) - float(m.relative_alt))/ 1000
            if len(self.plane_gps_history) >= SDAModule.MAX_PLANE_LOCATION_DATA_POINTS:
                self.plane_gps_history.popleft()
            self.plane_gps_history.append(item)

            if len(self.plane_gps_history) > 1 and Data.currentWPIndex > 0 and self.sda_on:
                try:
                    #self.run_sda_computations()
                    pass
                except Exception as e:
                    # catches error, gives stack trace and line number of error
                    traceback.print_exc()


    def run_sda_computations(self, waypoints):
        self.populate_waypoint_list(waypoints)
        start_pos_as_wp = self.wplist[0]
        self.wplist = self.wplist[1:]
        plane_xyz = np.array([start_pos_as_wp.x, start_pos_as_wp.y, start_pos_as_wp.z])
        print (plane_xyz)
        # BAD CODE - USED TO BE NP ARRAY. NOW WERE USING A NUMBER
        plane_v = self.estimated_speed
        if self.active_listener_thread == None:

            parent_conn, child_conn = multiprocessing.Pipe()
            t = threading.Thread(target=self.waypoint_update_listener, args=(parent_conn,))
            t.daemon = True
            self.active_listener_thread = t
            p = multiprocessing.Process(target=self.adjust_flight_path_to_avoid_obstacles, args=(child_conn, plane_xyz, plane_v, self.path_dict))
            self.current_process = p
            self.all_processes.append(p)
            p.start()
            child_conn.close()
            t.start()
        else:
            raise Exception("active listener thread not inactive")
        return t

    def populate_waypoint_list(self, waypoints):
        self.convert.set_zero_coord(waypoints[0]['lat'], waypoints[0]['lon'])
        for wp in waypoints[1:]:
            alt = wp['alt'] + self.base_alt
            wp_xyz = np.array(self.convert.ll2m(wp['lat'], wp['lon']) + [alt])
            self.wplist.append(mp_geo.Waypoint(wp_xyz[0], wp_xyz[1], wp_xyz[2], sda=wp['sda']))

    def sda_enabled(self):
        return self.sda_on

    # REPLACED BINDING
    def enable_sda(self):
        if not self.is_bound:
            interop.get_instance().bind_to_new_obstacle(self.pdriver.update_obstacles_from_interop)
            self.is_bound = True
        self.sda_on = True

    def get_sda_suggestions(self, start_i, end_i):
        print ("suggesting for ", start_i, end_i)
        home_wp = mavproxy_database.get_db_mod().get_wps()[0]
        wps = [home_wp] + filter(lambda x: not x['sda'], mavproxy_database.get_db_mod().get_wps()[start_i:end_i + 1])
        print ("wps", len(wps))
        listener_thread = self.run_sda_computations(wps)
        listener_thread.join()
        print ("finished suggesting")
        print ([wp['command'] for wp in wps])
        first_wp, original_wps = wps[1], wps[2:]
        final_wplist = self.wplist
        self.wplist = []
        print ("final wps", self.get_waypoint_list_as_dict(final_wplist, original_wps, first_wp))
        return self.get_waypoint_list_as_dict(final_wplist, original_wps, first_wp)

    def get_waypoint_list_as_dict(self, wplist, original_wps, first_wp):
        first_wp['sda'] = False
        wp_dicts = [first_wp]
        i = 0
        for wp in wplist:
            wp_d = {}
            c = self.convert.m2ll(wp[0], wp[1])
            wp_d['lat'], wp_d['lon'] = c['lat'], c['lon']
            wp_d['alt'] = wp[2] - self.base_alt
            wp_d['sda'] = wp.sda
            if wp.sda:
                wp_d['command'] = 16
            else:
                wp_d['command'] = original_wps[i]['command']
                i += 1
            wp_dicts.append(wp_d)
        return wp_dicts

    
    # TODO: TEST
    def get_geofence(self):
        if len(self.fenceloader) < 1:
            return
        fence_list = []
        for i in range(0, len(self.fenceloader)):
            fence_list.append(tuple(self.convert.ll2m(self.fenceloader[i].x, self.fenceloader[i].y)))
               
        self.fence = mp_geo.Geofence(fence_list)

    
    # NOT USED
    # DEPRECIATED
    def get_waypoint_list(self):
        self.wplist = []
        for i, wp in enumerate(Data.wplist): 
            try: 
                wp_cpy = copy.deepcopy(wp)
                if i == 0:
                    self.convert.set_zero_coord(wp_cpy.x, wp_cpy.y)
                else: 
                    wp_cpy.z += self.base_alt
                wp_xyz = np.array(self.convert.ll2m(wp_cpy.x, wp_cpy.y) + [wp_cpy.z])
                self.wplist.append(mp_geo.Waypoint(wp_xyz[0], wp_xyz[1], wp_xyz[2], sda=wp.sda, mav_wp=wp)) 
            except Exception as e:
                # catches error, gives stack trace and line number of error
                exc_type, _, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error("Error "+str(e)+' '+str(exc_type)+' '+str(fname)+' '+str(exc_tb.tb_lineno))
    
    def update_obstacles(self):
        stationary_obstacles = interop.get_instance().get_obstacles()['stationary_obstacles']
        self.pdriver.update_obstacles(stationary_obstacles)

    # NOT USED
    def get_position_and_velocity_in_rectangular_coords(self):
        plane_xy = self.convert.ll2m(float(Data.pdata['GLOBAL_POSITION_INT'].lat)/pow(10,7), float(Data.pdata['GLOBAL_POSITION_INT'].lon)/pow(10,7))       
        #write_to_sda_log(plane_xy)
        ## get plane position and velocity, convert alt to meters, everything is in absolute altitudes
        plane_xyz = np.array([plane_xy[0], plane_xy[1], float(Data.pdata['GLOBAL_POSITION_INT'].alt) / 1000])
        plane_v = self.getInstantaneousVelocity(self.plane_gps_history[-2], plane_xyz, time=time.time())
        return plane_xyz, plane_v

    # TODO: TEST
    # Run on new mavlink packets
    def adjust_flight_path_to_avoid_obstacles(self, pipe, plane_xyz, plane_v, path_dict):
        try: 
            # current perminant waypoint index
            #perm_waypoints = [x for x in self.wplist if not x.sda]
            prev_perm_waypoint = None
            #cwpi = Data.currentWPIndex
            #while self.wplist[cwpi].sda == True:
            #    cwpi += 1
            current_perm_waypoint = self.wplist[0]

            # if we added any waypoints throughout the entire lookahead process
            waypoint_path_changed = False
            # BAD CODE 
            init_heading = mp_geo.unit_vector(np.array([plane_v, 0, 0]))
            time_stamp = 0
            # BAD CODE 
            self.rrt.speed = plane_v
            # BAD CODE
            for i in range(len(self.wplist)):  
                print ("i", i)
                if prev_perm_waypoint is not None:
                    plane_xyz = prev_perm_waypoint.dv

                self.update_obstacles()
                
                if not current_perm_waypoint in path_dict:
                    path_dict[current_perm_waypoint] = []
                #log_update_message('\n\niteration: ' + str(i) + ' current perm waypoint index: ' + 
                #str(self.wplist.index(current_perm_waypoint)), 'path_dict.debug')
                #log_waypoint_dict(path_dict, 'path_dict.debug')
                print ("preupdate")
                rrt_wp_lst, did_update_flight_path, final_heading, time_stamp = self.rrt.generate_path_to_destination(plane_xyz, 
                                                                                            current_perm_waypoint.dv, 
                                                                                            [], 
                                                                                            init_heading, 
                                                                                            time_stamp)
                print ("did update", did_update_flight_path)
                # For all look-ahead waypoints, the final heading to the last waypoint is the 
                # init heading for the next waypoint
                if final_heading is not None:
                    init_heading = final_heading
                else: 
                    break
                if did_update_flight_path:
                    waypoint_path_changed = True
                    path_dict[current_perm_waypoint] = self.path_dict_manager.list(rrt_wp_lst)
                    # flight_path_waypoints = self.path.smooth_path(rrt_wp_lst)
                    flight_path_waypoints = rrt_wp_lst
                    # print "index of current perm waypoint", self.wplist.index(current_perm_waypoint)
                    self.update_path_to_wp_at_index(flight_path_waypoints, self.wplist.index(current_perm_waypoint))
                
                prev_perm_waypoint = current_perm_waypoint
                if not self.wplist.index(current_perm_waypoint) < len(self.wplist) - 1:
                    break

                current_perm_waypoint = self.wplist[self.wplist.index(current_perm_waypoint) + 1] 
                
            if waypoint_path_changed:
                # Sending the waypoints to the main process to be sent to the plane
                pipe.send((self.wplist, len(self.wplist), rrt_wp_lst, current_perm_waypoint))
            # otherwise No new information, just close the pipe and finish 
        except Exception as e:
            # catches error, gives stack trace and line number of error
            traceback.print_exc()
            print ("************************************************************")
            print ("************************************************************")
            print ("ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR ")
            print ("setting to none because error")
            print ("************************************************************")
            print ("************************************************************")
            print ("\n\n")
            # allow other threads to be instantiated 
            self.active_listener_thread = None
            self.current_process = None

        finally: 
            pipe.close()

    # TODO: TEST
    def update_path_to_wp_at_index(self, path, index):
        init_wp_inidex = index
        final_wp_index = index
        while self.wplist[init_wp_inidex-1].sda == True:
            init_wp_inidex -= 1
        self.wplist = self.wplist[:init_wp_inidex] + path + self.wplist[final_wp_index:]

    
    def getInstantaneousVelocity(self, p1, p2, time):
        delta_time = time - p1['time']

        # sometimes lon and lat are given as a number times 10^7
        if abs(p1['lat']) > 1000:
            xy1 = self.convert.ll2m(p1['lat']/pow(10,7), p1['lon']/ pow(10,7))
            p1_alt = p1['alt']
            p2_alt = p2[2]
        else:
            xy1 = self.convert.ll2m(p1['lat'], p1['lon'])
            p1_alt = p1['alt']
            p2_alt = p2[2]

        vx = (p2[0] - xy1[0]) / delta_time
        vy = (p2[1] - xy1[1]) / delta_time
        vz = (p2_alt - p1_alt) / delta_time

        return np.array([vx, vy, vz])

    def waypoint_update_listener(self, pipe): 
        try:
            wps, num_wp, rrt_wps, current_wp = pipe.recv()

            assert len(wps) == num_wp
            self.path_dict[current_wp] = rrt_wps
            #log_update_message('path updated to have ' + str(len(self.path_dict)) + ' entries', 'path_dict.debug')
            print ("listener wps", wps)
            self.wplist = wps 
            #self.add_all_sda_waypoints_to_data()
        except EOFError as err:
            pass
        except (KeyboardInterrupt, SystemExit):
            if self.current_process != None:
                self.current_process.terminate()
        finally:
            self.active_listener_thread = None
            self.current_process = None

    def add_all_sda_waypoints_to_data(self):
        #print time.time()
        mavproxy_wp.get_wp_mod().wploader.clear() 
        for wp in self.wplist:
            if wp.sda:
                latlng = self.convert.m2ll(wp[0], wp[1])
                alt = wp[2] - self.base_alt
                
                # create a waypoint
                command = 16

                mavproxy_wp.get_wp_mod().wploader.target_system = mavproxy_wp.get_wp_mod().wploader.target_system
                mavproxy_wp.get_wp_mod().wploader.target_component = mavproxy_wp.get_wp_mod().wploader.target_component
                frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
                p = mavutil.mavlink.MAVLink_mission_item_message(mavproxy_wp.get_wp_mod().wploader.target_system,
                                                                 mavproxy_wp.get_wp_mod().wploader.target_component,
                                                                 0,
                                                                 frame,
                                                                 command,
                                                                 0, 1, 0, 0, 0, 0,
                                                                 latlng['lat'], latlng['lon'], alt, sda=wp.sda)
                mavproxy_wp.get_wp_mod().wploader.add(p)
            else:
                mavproxy_wp.get_wp_mod().wploader.add(wp.mav_wp)
        mavproxy_wp.get_wp_mod().wploader.reindex() 
        mavproxy_wp.get_wp_mod().send_all_waypoints()
        mavproxy_wp.get_wp_mod().wploader.expected_count = len(self.wplist)
        mavproxy_wp.get_wp_mod().wp_set_current(Data.currentWPIndex)

    # *****************************************************************

    # ERROR: Waypoint altitudes get jumbled when this happens. Fix this 
    
    # *****************************************************************

    def disable_sda(self):
        self.sda_on = False
        self.path_dict = self.path_dict_manager.dict()
        
instance = None
def write_to_sda_log(loc):
    with open('sda_log.txt', 'a') as f:
        f.write(str(loc[0]) + ' , ' + str(loc[1]) + '\n')

def log_waypoint_dict(my_dict, file_name):
    with open(file_name, 'a') as f:
        f.write('*******************\n')
        for point, waypoints in my_dict.items():
            f.write('------\n')
            f.write('point ' + str(point.dv[0]) + ', ' + str(point.dv[1]) + ', ' + str(point.dv[2]) + '\n')
            for wp in waypoints:
                f.write(str(wp.dv[0]) + ', ' + str(wp.dv[1]) + ', ' + str(wp.dv[2]) + '\n')

def log_update_message(message, file_name):
    with open(file_name, 'a') as f:
        f.write(str(message) + '\n')

def get_sda_mod():
    global instance
    if (instance is None):
        raise Exception("SDAModule Not Initialized")
    return instance

def init(mpstate):
    '''initialise module'''
    global instance
    instance = SDAModule(mpstate)
    return instance
