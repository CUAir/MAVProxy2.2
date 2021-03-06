import bezier.curve as bc
from modules.lib import mp_module
from modules import mavproxy_database
from modules import mavproxy_mission
import numpy as np
import json
import time
# import modules.mavproxy_sda.sda_util as sda_util
import mavproxy_logging
from modules.server.views.views_utils import json_serial

logger = mavproxy_logging.create_logger("sda_plane_pred")
class PlanePredictionModule(mp_module.MPModule):

    def __init__(self, mpstate, step=1):
        super(PlanePredictionModule, self).__init__(mpstate, "plane_prediction", "sda module", public=True)
        self.curr_waypoint_index = -1
        self.waypoints = []
        self.waypoint_times =[]
        self.curves = []
        self.curve_end_times = []
        self.step_time = step
        self.initialize_convert()
        self.mission_module = mavproxy_mission.get_mission_mod()
        self.last_update = -float("inf")
        self.min_update_time = 1 #number of seconds between updates (cannot update splines if they were updated less than this time ago)

    def update_waypoints(self,tm=None):
        db = mavproxy_database.get_db_mod()
        wps = mavproxy_database.get_db_mod().get_waypoints()
        self.curr_waypoint_index = mavproxy_database.get_db_mod().get_current_wp()
        if len(wps) == 0:
            return
        
        # update waypoints and convert to meters
        self.waypoints = []
        for wp in wps:
            lat = wp['lat']
            lon = wp['lon']
            self.waypoints.append(np.array(self.convert.ll2m(lat,lon)))

    def get_speed_and_pos(self,tm=None):
        gps_status = mavproxy_database.get_db_mod().get_gps(tm)
        vx = gps_status["groundvx"]
        vy = gps_status["groundvy"]
        lat = gps_status["lat"]
        lon = gps_status["lon"]
        return (np.sqrt(vx**2 + vy**2),lat,lon)

    def get_current_path(self,lat,lon):
        path = self.mission_module.spline_path
        if path != []:
            cps = path[-1]
            cp1 = self.convert.ll2m(cps[0]['lat'],cps[0]['lon'])
            cp2 = self.convert.ll2m(cps[1]['lat'],cps[1]['lon'])
            cp3 = self.convert.ll2m(cps[2]['lat'],cps[2]['lon'])
            cp4 = self.convert.ll2m(cps[3]['lat'],cps[3]['lon'])
            return bc.Curve(np.array([cp1,cp2,cp3,cp4]),3)
        else:
            wp = self.waypoints[self.curr_waypoint_index]
            cp1 = self.convert.ll2m(lat,lon)
            cp2 = wp[0],wp[1]
            return bc.Curve(np.array([cp1,cp2]),1)

    def gen_curves(self):
        if ((time.time() - self.last_update) < self.min_update_time): #splines were updated recently
            return
        self.last_update = time.time()
        self.curves = []
        self.curve_end_times = []
        speed,lat,lon = self.get_speed_and_pos()
        #initalized to the curve we are currently flying
        prev_curve = self.get_current_path(lat,lon)
        #added current curve to curves
        self.curves.append(prev_curve)
        #store the end time of the current curve
        prev_end_time = self.gen_curve_time(speed,prev_curve)
        #make the endtime be the end time of the current curve
        #in other words, make the start time of the current curve time 0 for further calculations
        self.curve_end_times.append(prev_end_time)
        #removed previous waypoints
        upcoming_waypoints = self.waypoints[self.curr_waypoint_index:]
        if (len(upcoming_waypoints) >= 3):
            for wp1,wp2,wp3 in zip(upcoming_waypoints,upcoming_waypoints[1:],upcoming_waypoints[2:]):    
                #approximate heading at end of the previous curve
                approx_heading_not_normalized = prev_curve.evaluate(1.0) - prev_curve.evaluate(0.95)
                heading = approx_heading_not_normalized / np.linalg.norm(approx_heading_not_normalized)
                velocity = (heading * speed).flatten()
                curve = self.gen_curve_from_waypoint_triple(wp1,wp2,wp3,velocity)
                curr_time = prev_end_time + self.gen_curve_time(speed,curve)
                self.curves.append(curve)
                self.curve_end_times.append(curr_time)
                prev_curve = curve
                prev_end_time = curr_time
        #handles linear interpolation for last two waypoints, when not currently
        #flying towards the last waypoint
        if len(upcoming_waypoints) > 1:
            last_wp = self.waypoints[-1]
            second_to_last_wp = self.waypoints[-2]
            cp1 = second_to_last_wp[0],second_to_last_wp[1]
            cp2 = last_wp[0],last_wp[1]
            curve = bc.Curve(np.array([cp1,cp2]),1)
            self.curves.append(curve)
            curr_time = prev_end_time + self.gen_curve_time(speed,curve)
            self.curve_end_times.append(curr_time)

    def gen_curve_from_waypoint_triple(self,wp1,wp2,wp3,ground_vel):
        cp1 = float(self.mpstate.public_modules["param"].get_mav_param("NAVSP_CP2_SEC")) * ground_vel + wp1
        goal_traj = wp3 - wp2
        scaling_factor = 150 / (np.linalg.norm(goal_traj) ** 2)
        offset = -goal_traj * np.linalg.norm(ground_vel) * float(self.mpstate.public_modules["param"].get_mav_param("NAVSP_CP3_SEC")) * scaling_factor
        cp2 = wp2 + offset
        curve = bc.Curve(np.array([wp1,cp1,cp2,wp2]),3)
        return curve

    # returns the time to fly a particular curve given a constant flight speed 
    def gen_curve_time(self,speed,curve):
        if speed == 0.0:
            raise ValueError("Time cannot be computed with zero speed")
        return curve.length / speed

    # computes the time for a curve given the index of the curve, used to avoid errors when velocity
    # changes after curve has been computed
    def get_curve_time(self,curve_index):
        if self.curves is None:
            raise Exception("No curves created")
        elif curve_index > len(self.curves):
            raise Exception("Curve index out of range")
        #this is a degenerate case
        if curve_index < 0:
            raise Exception("invalid curve index")
        elif curve_index == 0:
            return self.curve_end_times[0]
        else:
            return self.curve_end_times[curve_index] - self.curve_end_times[curve_index - 1]

    def get_pos_at_time(self,t):
        prev_time = 0
        speed,lat,lon = self.get_speed_and_pos()
        for i in range(len(self.curve_end_times)):
            if self.curve_end_times[i] >= t:
                diff = t - prev_time
                scaled_time = diff / (self.get_curve_time(i))
                return self.curves[i].evaluate(scaled_time)
            else:
                prev_time = self.curve_end_times[i]
        print(self.curve_end_times)
        raise Exception("Plane path not long enough")

    def get_path_points_and_times(self):
        self.gen_curves()
        speed,lat,lon = self.get_speed_and_pos()

        x,y = self.convert.ll2m(lat,lon)
        #start time is time in the reference frame of the curves
        # In other words, time 0 is the time the plane hit the last waypoint
        start_time = self.get_approx_time_on_curve(0,np.array([x,y]))
        # the actual current time, both times are used to calculate the real time 
        # at which the plane will be at various points
        real_start_time = time.time()
        t = start_time
        end_time = self.curve_end_times[-1]
        time_point_pairs = []

        while t <= end_time:
            real_time = (t - start_time) + real_start_time
            position_at_time = self.get_pos_at_time(t)
            lat_lon = self.convert.m2ll(position_at_time[0,0],position_at_time[0,1])
            lat = lat_lon['lat']
            lon = lat_lon['lon']
            time_point_pairs.append((real_time,(lat,lon)))
            t += self.step_time
        return time_point_pairs

    # returns the approximate time the plane has flown along the curve at curve_index
    # step is the granuality for computing the parameter t relating to the bezier curve.
    def get_approx_time_on_curve(self,curve_index,point,step=0.01):
        curve = self.curves[curve_index]
        min_time = 0
        min_dist = float("inf")
        t = 0.0
        while t <= 1:
            point_at_t = curve.evaluate(t)
            dist = np.linalg.norm(point_at_t - point)
            if min_dist > dist:
                min_dist = dist
                min_time = t
            t += step
        return min_time * self.get_curve_time(curve_index)

    def get_plane_state(self):
        path = self.get_path_points_and_times()
        return json.dumps(path)

    def initialize_convert(self):
        wps = mavproxy_database.get_db_mod().get_waypoints()
        if wps == []:
            self.convert = None
            return False
        else:
            base_wp = wps[0]
            lat = base_wp['lat']
            lon = base_wp['lon']
            # self.convert = sda_util.Convert(lat,lon)
            return True

    def check_precondition(self):
        if self.convert is None:
            initialized = self.initialize_convert()
            if not initialized:
                return False
        self.update_waypoints()
        threshold = 0.1
        if self.curr_waypoint_index <= 0:
            return False
        if (len(self.waypoints) < 3):
            return False
        speed,lat,lon = self.get_speed_and_pos()
        if speed <= 0.0:
            return False
        return True

    def gps_prediction(self,tm):
        if tm is not None:
            tm = float(tm)/1000
        else:
            try:
                gps = mavproxy_database.get_db_mod().get_gps(tm)
                if gps is not None:
                    return json.dumps(gps,default=json_serial)
                else:
                    return "No Content", 204
            except Exception as e:
                logger.error(e)
                return "Error, could not predict plane data", 412
        try:
            valid = self.check_precondition()
            if valid and tm > time.time():
                    self.gen_curves()
                    gps = mavproxy_database.get_db_mod().get_gps(None)
                    xy = self.get_pos_at_time(tm - time.time())
                    xy = xy.flatten()
                    x = xy[0]
                    y = xy[1]
                    lat_lon = self.convert.m2ll(x,y)
                    lat = lat_lon['lat']
                    lon = lat_lon['lon']
                    gps['lat'] = lat
                    gps['lon'] = lon
                    gps['time'] = tm
                    return json.dumps(gps)
            else:
                gps = mavproxy_database.get_db_mod().get_gps(tm)
                if gps is not None:
                    return json.dumps(gps,default=json_serial)
                else:
                    return "No Content", 204
        except Exception as e:
            logger.error(e)
            return "Error, could not predict plane data", 412
instance = None
def get_sda_plane_pred_mod():
    global instance
    if (instance is None):
        raise Exception("PlanePredictionModule Not Initialized")
    return instance

def init(mpstate):
    '''initialise module'''
    global instance
    instance = PlanePredictionModule(mpstate)
    return instance

