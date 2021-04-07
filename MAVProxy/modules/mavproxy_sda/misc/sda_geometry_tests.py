import unittest
import numpy as np
import math
from modules.sda_geometry import *

p1 = Point(1,2,3)
p2 = Point(0,0,0)
p3 = Point(-1,-2,-3)
p4 = Point(1,1,1)

def float_eq(x, y):
    return abs(x - y) < .0001

class Test_Point(unittest.TestCase):

    def test_construction(self):
        test_point = Point(1,2,3)
        self.assertTrue(test_point.x == 1 and test_point.y == 2 and test_point.z == 3 and np.array_equal(test_point.dv, np.array([1,2,3])))
        test_point = Point(np_array=np.array([1,2,3]))
        self.assertTrue(test_point.x == 1 and test_point.y == 2 and test_point.z == 3 and np.array_equal(test_point.dv, np.array([1,2,3])))

    def test_add_points(self):
        self.assertTrue(p1 + p2 == p1)
        self.assertTrue(p1 + p3 == p2)
        self.assertTrue(p2 + p2 == p2)

    def test_subtract_points(self):
        self.assertTrue(p1 - p2 == p1)
        self.assertTrue(p2 - p2 == p2)
        self.assertTrue(p3 - p3 == p2)

    def test_mult_points(self):
        self.assertTrue(p1.mult(0) == p2)
        self.assertTrue(p1.mult(1) == p1)
        self.assertTrue(p4.mult(1) == p4)

    def test_distance(self):
        self.assertTrue(p2.distance(p2) == 0)
        self.assertTrue(float_eq(p4.distance(p2), math.sqrt(3)))
        self.assertTrue(float_eq(p1.distance(p3), math.sqrt(56)))
        self.assertTrue(float_eq(p4.distance(p1), math.sqrt(5)))

class Test_Line(unittest.TestCase):

    #Constructor is super simple - literally just assignments, no need to test it

    def test_line_to_point_distance(self):
            print Line(Point(1,0,0), Point(-1,0,0)).distance(Point(0,1,0))
            self.assertTrue(Line(Point(1,0,0), Point(-1,0,0)).distance(Point(0,1,0)) == 1)
            #self.assertTrue(Line(Point(0,1,0), Point(1,0,0)).distance(Point(1,2,1)) == math.sqrt(2))

class Test_Segment(unittest.TestCase):

    #Constructor is super simple - literally just assignments, no need to test it

    def test_intersect(self):
            s1 = Segment(Point(-1, 0, 0), Point(1, 5, 0))
            s2 = Segment(Point(-1, 4, 0), Point(1, 4, 0))
            s3 = Segment(Point(-10, 4, 0), Point(-5, 4, 0))
            self.assertTrue(not s1.intersect(s3))
            self.assertTrue(s1.intersect(s2))
            
        

if __name__ == '__main__':
    unittest.main()