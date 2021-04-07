from modules.mavproxy_sda.sda_util import Convert
import mavproxy_logging
import numpy as np

from modules.mavproxy_path_planning.algorithms.potential_flow import PotentialFlow
# from modules.mavproxy_path_planning.algorithms.gradient_based import GradientBased
from modules.mavproxy_database import get_db_mod
from modules.mavproxy_wp import get_wp_mod
from modules.lib import mp_module
import modules.mavproxy_interop.interop as interop
import time 
import shapely.geometry as sg
instance = None

logger = mavproxy_logging.create_logger("path_planning")

class PathPlanningModule(mp_module.MPModule):
    def __init__(self, mpstate):
        super(PathPlanningModule, self).__init__(mpstate, "path_planning", "path planning module", public=True)

    def plan_path(self, route_wp_indices, buf, prev_wp=None, height_buf=5):
        # Initializing the starting waypoint
        start_wp_id = route_wp_indices[0]
        start_wp_meters = self.converter.ll2m(self.waypoints[start_wp_id]['lat'],
                                               self.waypoints[start_wp_id]['lon'])
        start_wp = np.asarray(start_wp_meters)

        # Initializing the ending waypoint
        end_wp_id = route_wp_indices[1]
        end_wp_meters = self.converter.ll2m(self.waypoints[end_wp_id]['lat'],
                                             self.waypoints[end_wp_id]['lon'])
        end_wp = np.asarray(end_wp_meters)

        # Initializing the previous waypoint to find smoother paths
        if not prev_wp is None:
            prev_wp_meters = self.converter.ll2m(prev_wp['lat'], prev_wp['lon'])
            prev_wp = np.asarray(prev_wp_meters)

        # Removing all the obstacles which are not within the height of wps
        curr_obstacles = []
        wp_min_alt = min(self.waypoints[start_wp_id]['alt'],self.waypoints[end_wp_id]['alt'])
        for obs in self.obstacles:
            # height buf is in meters 
            if wp_min_alt - obs[-1] <= height_buf:
                curr_obstacles.append(obs)
        curr_obstacles = np.asarray(curr_obstacles)

        # Initializing the path planning algorithm
        planner = PotentialFlow(geofence=self.geofence, obstacles=curr_obstacles, buf=buf)
        path = planner.plan(start_wp, end_wp, prev_wp=prev_wp)

        # Interpolte the altitudes of the wp
        new_wps = self.interpolate_wp_alt(self.waypoints[start_wp_id], 
                                          self.waypoints[end_wp_id], 
                                          path, [], self.converter)
        return new_wps

    def plan(self, route_wp_indices, geofence, buf):
        logger.info("Starting SDA")
        self.waypoints = get_db_mod().get_waypoints()
        self.converter = Convert(self.waypoints[0]['lat'], self.waypoints[0]['lon'])

        if len(geofence) < 2:
            geofence = [[38.1462694444 ,-76.4281638889],
                        [38.151625 ,-76.4286833333],
                        [38.1518888889 ,-76.4314666667],
                        [38.1505944444 ,-76.4353611111],
                        [38.1475666667 ,-76.4323416667],
                        [38.1446666667 ,-76.4329472222],
                        [38.1432555556 ,-76.4347666667],
                        [38.1404638889 ,-76.4326361111],
                        [38.1407194444 ,-76.4260138889],
                        [38.1437611111 ,-76.4212055556],
                        [38.1473472222 ,-76.4232111111],
                        [38.1461305556 ,-76.4266527778],
                        ] 

        geofence_list = []
        for point in geofence:
            geofence_list.append(self.converter.ll2m(point[0], point[1]))
        self.geofence = sg.Polygon(geofence_list)
        logger.critical(self.geofence)
        # Initializing the obstacles
        obstacles = interop.get_instance().get_obstacles()['stationary_obstacles']
        obstacle_list = []
        for obstacle in obstacles:
            x,y = self.converter.ll2m(obstacle['latitude'], 
                                      obstacle['longitude'])
            # Interop gives this in feet but our backend converts to meter
            radius = obstacle['radius']
            # Interop gives this in feet but our backend converts to meter
            height = obstacle['height']
            obstacle_list.append([x, y, radius, height])

        self.obstacles = np.asarray(obstacle_list)
        new_wps = []
        # Prepending the waypoints before route_wp_indices[0]
        for i in range(route_wp_indices[0]):
            parsed_wp = self.parse_wp(self.waypoints[i])
            new_wps.append(parsed_wp)

        # Path planning between waypoints
        for i in range(route_wp_indices[0], route_wp_indices[1]):
            new_wps.append(self.parse_wp(self.waypoints[i]))
            prev_wp = None
            if len(new_wps) > 1:
                prev_wp = new_wps[-2]

            logger.info("Planning between {} and {}".format(i,i+1))

            if self.is_wp_in_obstacle(i):
                # Add frontend thingy
                logger.info("Ignoring waypoint {} as it is inside an obstacle.".format(i))
                continue
            if self.is_wp_in_obstacle(i+1):
                # Add frontend thingy
                logger.info("Ignoring waypoint {} as it is inside an obstacle.".format(i+1))
                continue

            new_wps += self.plan_path([i, i+1], buf, prev_wp=prev_wp)
            logger.info("Planned between {} and {}".format(i,i+1))

        # Appending the waypoints after route_wp_indices[0]
        for i in range(route_wp_indices[1], len(self.waypoints)):
            parsed_wp = self.parse_wp(self.waypoints[i])
            new_wps.append(parsed_wp)

        get_wp_mod().wp_send_list(new_wps)
        logger.info("SDA Done")

    def is_wp_in_obstacle(self, i):
        if len(self.obstacles) > 0:
            wp = np.asarray(self.converter.ll2m(self.waypoints[i]['lat'],self.waypoints[i]['lon']))
            dist = np.linalg.norm(self.obstacles[:,:2] - wp, axis=1) - self.obstacles[:,2]
            return np.any(dist <= 0)
        else:
            return False

    def interpolate_wp_alt(self, start_wp, end_wp, path, new_wps, converter):
        start_alt = start_wp['alt']
        start_lat, start_lon = start_wp['lat'], start_wp['lon']

        end_alt = end_wp['alt']
        end_lat, end_lon = end_wp['lat'], end_wp['lon']

        for p in path:
            x,y = p[0], p[1]
            lat_lon = converter.m2ll(x,y)
            lat,lon = lat_lon['lat'],lat_lon['lon']
            dist_from_start = np.sqrt((start_lat - lat)**2 + (start_lon - lon)**2)
            dist_from_end = np.sqrt((end_lat - lat)**2 + (end_lon - lon)**2)
            total_dist = dist_from_end + dist_from_start
            alt = (start_alt*dist_from_end + end_alt*dist_from_start)/total_dist

            wp_as_dict = {'command': 16,'current': 0,'lat': lat,'lon': lon,'alt': alt, 'sda': 1}
            new_wps.append(wp_as_dict)

        return new_wps
    
    def delete_sda_wp(self):
        self.waypoints = get_db_mod().get_waypoints()
        wp_list = []
        for wp in self.waypoints:
            if wp['param1'] == 0:
                wp_list.append(self.parse_wp(wp))
        get_wp_mod().wp_send_list(wp_list)
        

    def parse_wp(self, waypoint):
        parsed_wp = {'command': waypoint['command'], 
                     'current': waypoint['current'], 
                     'lat': waypoint['lat'], 
                     'lon': waypoint['lon'], 
                     'alt': waypoint['alt'],
                     'sda': waypoint['param1']}
        return parsed_wp

def get_path_planning_mod():
    global instance
    if instance is None:
        raise Exception("Path Planning Module not initialized.")
    return instance

def init(mpstate):
    '''initialise module'''
    global instance
    instance = PathPlanningModule(mpstate)
    return instance
