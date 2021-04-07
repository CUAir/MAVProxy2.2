#!/usr/bin/env python
from collections import deque
from collections import namedtuple
from LatLon23 import Latitude, Longitude, LatLon
import math
import time
import numpy as np
import shapely.geometry as sg
import warnings

class DegenerateCaseException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

EPSILON = 0.000001
OBSTACLE_BUFFER = 0

def unit_vector(dv):
    if np.linalg.norm(dv) < EPSILON:
        return np.zeros(len(dv))
    return (1.0/math.sqrt(dv.dot(dv))) * dv

class Point(object):
    def __init__(self, x=None, y=None, z=None, np_array=None):
        if isinstance(x, np.ndarray):
            self.dv = x
            self.x = self.dv[0]
            self.y = self.dv[1]
            self.z = self.dv[2]
        elif isinstance(np_array, np.ndarray):
            if len(np_array) == 2:
                np_array = np.append(np_array, [0])
            self.dv = np_array
            self.x = np_array[0]
            self.y = np_array[1]
            self.z = np_array[2] 
        elif x is not None and y is not None and z is not None:
            self.x = x
            self.y = y
            self.z = z
            self.dv = np.array([x, y, z])
        elif x is not None and y is not None and z is None:
            self.x = x
            self.y = y
            self.z = 0
            self.dv = np.array([x, y, 0])
        else:
            raise Exception("Bad Constructor input!")

    def __add__(self, p):
        return Point(np_array=(self.dv + p.dv))

    def __sub__(self, p):
        return Point(np_array=(self.dv - p.dv))

    def __str__(self):
        return "Point: " + str(self.x) + ", " + str(self.y) + ", " + str(self.z)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, i):
        return self.dv[i]
    def mult(self, scalar):
        x = self.x * scalar
        y = self.y * scalar
        z = self.z * scalar
        return Point(np_array=np.array([x, y, z]))

    def distance(self, point):
        if isinstance(point, np.ndarray):
            return np.linalg.norm(self.dv - point) 
        return np.linalg.norm(self.dv - point.dv)   

    def __eq__(self, point):
        epsilon = .00001
        return abs(self.x - point.x) < epsilon and abs(self.y - point.y) < epsilon and abs(self.z - point.z) < epsilon

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __name__(self):
        return "Point"

class Line(object):
    def __init__(self, p1, p2):
        if isinstance(p1, np.ndarray):
            p1 = Point(np_array=p1)
        
        if isinstance(p2, np.ndarray):
            p2 = Point(np_array=p2)
        
        if not isinstance(p1, Point) or not isinstance(p2, Point):
            raise Exception("Error: " + str(p1) + " and " + str(p2) + " must be points!")
        self.p1 = p1
        self.p2 = p2
        self.dv = p2.dv - p1.dv


    def __str__(self):
        return "Line: " + str(self.p1) + ", " + str(self.p2)
    
    def distance(self, x):
        if isinstance(x, Line):
            p = x.p1
            q = self.p1
            n = np.cross(x.dv, self.dv)

            dist = np.linalg.norm(np.dot(p.dv-q.dv, n)) / np.linalg.norm(n)
            return dist
        elif isinstance(x, Point):
            proj = self.projection(x)
            return x.distance(proj)
        else: 
            raise TypeError("Bad type!: " + str(type(x)))
        # returns shortest distance to point
    
    def projection(self, point):
        AB = self.p2 - self.p1
        dot = np.dot(point.dv - self.p1.dv, AB.dv) / np.linalg.norm(AB.dv)**2
        proj = self.p1.dv + AB.mult(dot).dv
        return Point(np_array=proj)

    def closest_points(self, a0, a1, b0, b1, clampAll=False, clampA0=False, clampA1=False, clampB0=False, clampB1=False):
        ''' Given two lines defined by numpy.array pairs (a0,a1,b0,b1)
            Return distance, the two closest points, and their average
        '''
        # If clampAll=True, set all clamps to True
        if clampAll:
            clampA0 = True
            clampA1 = True
            clampB0 = True
            clampB1 = True

        # Calculate denomitator
        A = a1 - a0
        B = b1 - b0

        if np.linalg.norm(A - np.zeros(len(A))) < EPSILON:
            raise DegenerateCaseException()
        if np.linalg.norm(B - np.zeros(len(B))) < EPSILON:
            raise DegenerateCaseException()

        _A = A / np.linalg.norm(A)
        _B = B / np.linalg.norm(B)
        cross = np.cross(_A, _B)

        denom = np.linalg.norm(cross)**2

        # If denominator is 0, lines are parallel: Calculate distance with a projection
        # and evaluate clamp edge cases
        if (denom == 0):
            d0 = np.dot(_A, (b0-a0))
            d = np.linalg.norm(((d0*_A)+a0)-b0)
            # If clamping: the only time we'll get closest points will be when lines don't overlap at all.
            # Find if segments overlap using dot products.
            if clampA0 or clampA1 or clampB0 or clampB1:
                d1 = np.dot(_A, (b1-a0))
                # Is segment B before A?
                if d0 <= 0 >= d1:
                    if clampA0 is True and clampB1 is True:
                        if np.absolute(d0) < np.absolute(d1):
                            return b0, a0, np.linalg.norm(b0-a0)
                        return b1, a0, np.linalg.norm(b1-a0)
                # Is segment B after A?
                elif d0 >= np.linalg.norm(A) <= d1:
                    if clampA1 is True and clampB0 is True:
                        if np.absolute(d0) < np.absolute(d1):
                            return b0, a1, np.linalg.norm(b0-a1)
                        return b1, a1, np.linalg.norm(b1, a1)

            # If clamping is off, or segments overlapped, we have infinite results, just return position.
            return None, None, d

        # Lines criss-cross: Calculate the dereminent and return points
        t = (b0 - a0)
        det0 = np.linalg.det([t, _B, cross])
        det1 = np.linalg.det([t, _A, cross])

        t0 = det0/denom
        t1 = det1/denom

        pA = a0 + (_A * t0)
        pB = b0 + (_B * t1)

        # Clamp results to line segments if needed
        if clampA0 or clampA1 or clampB0 or clampB1:
            if t0 < 0 and clampA0:
                pA = a0
            elif t0 > np.linalg.norm(A) and clampA1:
                pA = a1

            if t1 < 0 and clampB0:
                pB = b0
            elif t1 > np.linalg.norm(B) and clampB1:
                pB = b1

        d = np.linalg.norm(pA-pB)

        return pA, pB, d

    def __name__(self):
        return "Line"

class Segment(Line):
    def __init__(self, p1, p2):
        if isinstance(p1, np.ndarray) and len(p1) == 2:
            p1 = np.append(p1, [0])
        if isinstance(p2, np.ndarray) and len(p2) == 2:
            p2 = np.append(p2, [0])
        Line.__init__(self, p1, p2)
        self.midpoint = (self.p2.dv - self.p1.dv)/2 + self.p1.dv

    def distance(self, x):
        if isinstance(x, Point):
            proj = Line(self.p1, self.p2).projection(x)
            cross = np.cross(self.p2.dv - self.p1.dv, proj.dv - self.p1.dv)
            assert(np.linalg.norm(cross) < 0.001)
            dot = np.dot(self.p2.dv - self.p1.dv, proj.dv - self.p1.dv) 
            if dot >= 0 and dot <= np.dot(self.p2.dv - self.p1.dv, self.p2.dv - self.p1.dv): 
                return proj.distance(x)
            else:
                return min(x.distance(self.p1), x.distance(self.p2))

        elif isinstance(x, Line):
            p1 = self.p1.dv
            p2 = self.p2.dv
            p3 = x.p1.dv
            p4 = x.p2.dv

            is_seg = isinstance(x, Segment)

            # TODO: Delete try except
            d = None
            try:
                pa, pb, d = x.closest_points(p1, p2, p3, p4, clampA0=True, clampA1=True, clampAll=is_seg)
            
            except Exception as e:
                # catches error, gives stack trace and line number of error
                exc_type, _, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error("Error "+str(e)+' '+str(exc_type)+' '+str(fname)+' '+str(exc_tb.tb_lineno))
            return d
        else: 
            raise TypeError("Bad type!: " + str(type(x)))
            
    def projection(self, point):
        AB = self.p2 - self.p1
        dot = np.dot(point.dv - self.p1.dv, AB.dv) / np.dot(AB.dv, AB.dv)
        proj = self.p1.dv + AB.mult(dot).dv
        
        #  yo jesse, proj is not a point, it's a nparray
        dot = np.dot(self.p2.dv - self.p1.dv, proj - self.p1.dv) 
        if dot >= 0 and dot <= np.dot(self.p2.dv - self.p1.dv, self.p2.dv - self.p1.dv): 
            return Point(np_array=proj)
        elif point.distance(self.p1) < point.distance(self.p2):
            return self.p1
        else:
            return self.p2

    # this is a 2d intersection function (for geofences)
    def intersect(self, line):
        if not isinstance(line, Segment):
            raise TypeError("Bad type!: " + str(type(line)))
        a0 = self.p1.dv
        a1 = self.p2.dv
        b0 = line.p1.dv
        b1 = line.p2.dv
        a0[2] = 0
        a1[2] = 0
        b0[2] = 0
        b1[2] = 0
        pa, pb, d = self.closest_points(a0, a1, b0, b1, clampAll=True)
        return d < .0001

    def intersection(self, line): 
        a0 = self.p1.dv
        a1 = self.p2.dv
        b0 = line.p1.dv
        b1 = line.p2.dv
        a0[2] = 0
        a1[2] = 0
        b0[2] = 0
        b1[2] = 0
        pa, pb, d = self.closest_points(a0, a1, b0, b1, clampAll=True)
        return pa 
        
    def __name__(self):
        return "Segment"

class Geofence:
    def __init__(self, points):
        self.polygon = sg.Polygon(points)

    def contains(self, x , y ):
        point = sg.Point(x,y)
        return self.polygon.contains(point)


    # TODO: TEST
    # returns point as tuple (x, y) within geofence
    def sample_random_point(self):
        minx, miny, maxx, maxy = self.polygon.bounds
        point = sg.Point((np.random.uniform(minx, maxx), np.random.uniform(miny, maxy)))
        while not self.polygon.contains(point):
            point = sg.Point((np.random.uniform(minx, maxx), np.random.uniform(miny, maxy)))
        return (point.x, point.y)

    # returns True iff the segment crosses the boundary of the geofence
    # @param segment = sda_util.Segment object
    def crosses(self, segment):
        p1 = segment.p1.dv
        p2 = segment.p2.dv
        points = [tuple(p1), tuple(p2)]
        return sg.LineString(points).crosses(self.polygon)

class Waypoint(Point):
    def __init__(self, x, y, z, sda=False, loiter=False, mav_wp=None):
        super(Waypoint, self).__init__(x=x, y=y, z=z)
        self.sda = sda
        self.loiter = loiter
        self.mav_wp = mav_wp

    def __add__(self, p):
        ''' you can't add waypoints '''
        raise NotImplementedError()

    def __sub__(self, p):
        ''' you can't subtract waypoints '''
        raise NotImplementedError()

    def __str__(self):
        return 'Waypoint: (' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')'

    def __repr__(self):
        waypoint = 'SDA Waypoint' if self.sda else 'Waypoint'
        return waypoint + ': (' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')'

    def __hash__(self):
        hash_str = str(int(self.x)) + str(int(self.y)) + str(int(self.z))
        return hash(hash_str)

    def __eq__(self, other):
        return (int(self.x), int(self.y), int(self.z)) == (int(other.x), int(other.y), int(other.z))

    def __ne__(self, other):
        return (int(self.x), int(self.y), int(self.z)) != (int(other.x), int(other.y), int(other.z))


class StationaryObstacle(Segment):
    def __init__(self, radius, position):
        # height is from 0 to z coordinate 
        super(StationaryObstacle, self).__init__(Point(x=position[0], y=position[1], z=0.0), position)
        self.radius = radius

    def intersects(self, path):
        if isinstance(path, Segment): 
            return path.distance(self) < self.radius + OBSTACLE_BUFFER
        else:
            raise Exception("Intersects not implemented for this input type")

ObstacleHistoryLoc = namedtuple('ObstacleHistoryLoc', ['time', 'x', 'y', 'z'])

class Convert:

    def __init__(self, zero_lat, zero_lon):
        self.zero_coordinate = LatLon(Latitude(zero_lat), Longitude(zero_lon))

    def set_zero_coord(self, zero_lat, zero_lon):
        new_zero = LatLon(Latitude(zero_lat), Longitude(zero_lon))
        if new_zero != self.zero_coordinate:
            self.zero_coordinate = new_zero

    def ll2m(self, lat, lon):
        """
        Converts latitude and longitude coordinates to relative corodinate system
        """
        p_latlon = LatLon(Latitude(lat), Longitude(lon))
        p_heading = math.radians(self.zero_coordinate.heading_initial(p_latlon))
        p_heading_vec = unit_vector(np.array([math.sin(p_heading), math.cos(p_heading)]))
        return list(p_heading_vec * self.zero_coordinate.distance(p_latlon) * 1000)

    def m2ll(self, x, y):
        """
        Converts coordinates in relative system to latitude and longitude coordinates
        """

        p_vec = np.array([x, y])

        p_dist = np.linalg.norm(p_vec) / 1000
        p_unit_vec = unit_vector(p_vec)
        p_heading = math.degrees(math.atan2(1, 0) - math.atan2(p_unit_vec[1], p_unit_vec[0]))
        ll_obj = self.zero_coordinate.offset(p_heading, p_dist)
        ll_lst = [float(x) for x in ll_obj.to_string('D')]
        return {'lat': ll_lst[0], 'lon': ll_lst[1]}

    @staticmethod
    def feet_2_meters(feet):
        return feet * 0.3048

convert_instance = Convert(0, 0)
