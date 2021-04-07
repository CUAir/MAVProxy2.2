from scipy.interpolate import splrep,splev

import collections
import numpy as np
import json
import time

from modules.lib import mp_module
from modules import mavproxy_database
import modules.mavproxy_interop.interop as interop
import modules.mavproxy_sda.sda_util as sda_util


import mavproxy_logging

# Rather than printing, we use 'logger.[debug|info|warning|error|critical]'
# This ensures that the output is color coded by severity, and also sent to a file if needed
# For debugging
logger = mavproxy_logging.create_logger("sda_pred")

class SDAPredictionModule(mp_module.MPModule):

    # initalizes an empty predictor with a buffer size of buffer_size, a buffer size of x indicates
    # that x obstacle data points must be obtained before updating the obstacle models to include these points
    # this prevents obstacles from recomputing splines to frequently
    def __init__(self, mpstate, buffer_size=10):
        super(SDAPredictionModule, self).__init__(mpstate, "obstacle_prediction", "sda module", public=True) 
        self.buffer_size = buffer_size
        self.buffer = []
        self.obstacles = []
        self.convert = sda_util.convert_instance
        #interop.get_instance().bind_to_new_obstacle(self.update_obstacles)
        self.center = None
    
    def add_obstacle(self, points, times, queue_len=None, update_queue_len=True):
        self.obstacles.append(ObstaclePredictor(points,times,queue_len,update_queue_len))

    # the precondtion is a precondition for being able to predict obstacle data
    # The precondition is that each obstacle has enough data points to compute splines and a period
    # If such data is not present, the model cannot produce predictions
    def check_precondition(self):
        return all(o.has_splines() for o in self.obstacles) and all(o.has_period() for o in self.obstacles)

    def predict_for_obstacle(self,id,step_size):
        return self.obstacles[id].get_period_and_points(step_size)

    def predict_points_for_obstacles(self,step_size=1):
        result = []
        if self.obstacles is None:
            raise ValueError("Cannot get obstacle data with no obstacles")
        for i in range(len(self.obstacles)):
            result.append(self.predict_for_obstacle(i,step_size))
        return result


    def get_obst_state(self):
        return json.dumps(self.predict_points_for_obstacles())

    def add_to_buffer(self, i, point, time):
        if len(self.buffer) < i:
            raise ValueError("obstacle data added in wrong order")
        if len(self.buffer) == i:
            self.buffer.append(([point],[time]))
        else:
            self.buffer[i][0].append(point)
            self.buffer[i][1].append(time)

    def flush_buffer(self):
        for i, (points, times) in enumerate(self.buffer):
            if len(self.obstacles) < i + 1:
                #TODO alter this to fill in other parameters
                self.add_obstacle(points,times)
            else:
                self.obstacles[i].add_points(points,times)
        self.buffer = []

class ObstaclePredictor:

    # note: variable length queue parameter unused as of now
    # if None is provided for points or times the fields will default to empty deques
    def __init__(self, points=None,times=None,queue_len=None,update_queue_len=True,period_buffer=5):
        self.period = None
        self.splx = None
        self.sply = None
        self.splz = None
        self.convert = sda_util.convert_instance
        self.period_buffer = period_buffer
        if queue_len is None:
            self.max_len = float("inf")
        else:
            self.max_len = queue_len

        self.vqueue = update_queue_len

        if points is None and times is None:
            self.points = collections.deque([])
            self.times = collections.deque([])
        elif points is None:
            raise ValueError("Cannot have times but lack points")
        elif times is None:
            raise ValueError("Cannot have points but lack times")
        elif len(points) != len(times):
            raise ValueError("Must have the same number of points and times")
        else:
            self.points = collections.deque([])
            self.times = collections.deque([])
            self.add_points(points,times)

    #updates the queues max length to l
    #TODO test or use this function
    def update_queue_len(self,l):
        self.max_len = l
        diff = l - len(self.points)
        if diff > 0:
            remove_points(diff)

    #finds the optimal period
    def update_period(self):
        points = self.points
        times = self.times
        if len(points) == 0:
            raise ValueError("Can't get the period with no points")
        head = points[0]
        first = times[0]
        l = len(points)
        i = 0
        min_error = float("inf")
        min_point = None
        min_time = None
        while i < l - 1:
            curr_point = points.pop()
            curr_time = times.pop()
            error = self.get_error(head,curr_point)
            # note the 5 is an arbitrary constant to keep from selecting very
            # small periods and getting stuck
            if (error < min_error and ((curr_time - first) > self.period_buffer)):
                min_error = error
                min_point = curr_point
                min_time = curr_time
            points.appendleft(curr_point)
            times.appendleft(curr_time)
            i += 1
        #append first element back on without getting its error
        points.appendleft(points.pop())
        times.appendleft(times.pop())
        if min_time is None:
            self.period = None
        else:
            self.period = min_time - times[0]
            self.min_error = min_error
    #gets euclidian distance between p1 and p2
    def get_error(self,p1,p2):
        return np.linalg.norm(p1 - p2)

    # adds ps and ts to the model for a given obstacle, requires len(ps) = len(ts)
    # points must come chronologically after points in the history, and be sorted by time-stamp
    # updates coresponding splines
    def add_points(self,ps,ts):
        l = len(self.points)
        if len(ps) > self.max_len:
            ps[len(ps) - self.max_len:] 
        diff = l + len(ps) - self.max_len
        if (diff > 0):
            self.remove_points(diff)
        for p,t in zip(ps,ts):
            self.points.append(p)
            self.times.append(t)

        self.update_splines()
        self.update_period()

    # removes n points and times from the left side of the queue does not update splines
    # used only for variable length queues
    def remove_points(self,n):
        while(n > 0):
            self.points.pop()
            self.times.pop()
            n -= 1

    #update splines corresponding to the points in the history
    def update_splines(self):
        if self.points is None or len(self.points) == 0 :
            raise ValueError("Must have a non-zero queue to get splines")
        xs,ys,zs = tuple(zip(*self.points))
        if len(self.points) < 4:
            d = len(self.points) - 1
            self.splx = splrep(self.times,xs,k=d)
            self.sply = splrep(self.times,ys,k=d)
            self.splz = splrep(self.times,zs,k=d)
        else:
            self.splx = splrep(self.times,xs)
            self.sply = splrep(self.times,ys)
            self.splz = splrep(self.times,zs)

    #guesses where the obstacle will be at time t
    def get_point(self,t):
        if self.splx is None or self.sply is None or self.splz is None:
            raise ValueError("Missing at least one of the 3 splines")
        if self.period is None:
            raise ValueError("No period to use")
        if t < 0:
            raise ValueError("Time cannot be negative")
        # time is the difference is the time to compute the obstacles position at
        # It is computed as the difference in the current time from the start time, mod 
        # the period of the obstacle     
        time = ((t - self.times[0]) % self.period) + self.times[0]
        x = float(splev(time,self.splx))
        y = float(splev(time,self.sply))
        z = float(splev(time,self.splz))
        pos = self.convert.m2ll(x,y)
        return pos["lat"],pos["lon"],z

    # gets a series of points starting at the first point, seperated 
    # by step, going through a full period
    def get_points(self,step,start):
        #TODO throw exceptions
        if self.splx is None or self.sply is None or self.splz is None:
            raise ValueError("No Splines to use")
        if self.period is None:
            raise ValueError("No period to use")
        result = []
        end = self.period + start
        curr = start
        while curr < end:
            result.append((curr,self.get_point(curr)))
            curr += step
        return result

    def get_period_and_points(self,step=1,start=None):
        if start is None:
            start = time.time()
        return (self.period,self.get_points(step,start))

    def has_splines(self):
        return (self.splx is not None and self.sply is not None and self.splz is not None)

    def has_period(self):
        return self.period is not None

instance = None
def get_sda_obst_pred_mod():
    global instance
    if (instance is None):
        raise Exception("SDAPrecitionModule Not Initialized")
    return instance

def init(mpstate):
    '''initialise module'''
    global instance
    instance = SDAPredictionModule(mpstate)
    return instance


        
