import unittest
import sda_path
import numpy as np

class SDAPathTests(unittest.TestCase):
    def test_calc_angular_error(self):
        spline = None # do not need spline for this test
        waypoint = sda_path.SmoothWaypoint(spline)
        p1 = np.array([1,2])
        p2 = np.array([3,4])
        p3 = np.array([-6,9])
        p4 = np.array([2,1])
        p5 = np.array([9,10])
        p6 = np.array([0,1])
        p7 = np.array([20,0])
        points_list = [p1,p2,p3,p4,p5,p6,p7]
        
        result = waypoint.calc_angular_error(0,4,points_list)
        self.assertAlmostEqual(result, 0.124355,5)

        result = waypoint.calc_angular_error(0,5,points_list)
        self.assertAlmostEqual(result, 0, 5)

        result = waypoint.calc_angular_error(2,5,points_list)
        self.assertAlmostEqual(result, 1.4289, 5)

        result = waypoint.calc_angular_error(4,6,points_list)
        self.assertAlmostEqual(result, 0.687857, 5)
    def test_calc_linear_error(self):
        spline = None
        waypoint = sda_path.SmoothWaypoint(spline)
        p1 = np.array([1,2,0])
        p2 = np.array([3,4,0])
        p3 = np.array([5,8,0])
        p4 = np.array([7,10,0])
        p5 = np.array([6,7,0])
        p6 = np.array([5,4,0])
        p7 = np.array([3,2,0])
        points_list = [p1,p2,p3,p4,p5,p6,p7]

        result = waypoint.calc_linear_error(0,4,points_list)
        self.assertAlmostEqual(result,3.16228,5)

        result = waypoint.calc_linear_error(3,0,points_list)
        self.assertAlmostEqual(result,0,0)

        result = waypoint.calc_linear_error(3,6,points_list)
        self.assertAlmostEqual(result,0.894427,5)

        result = waypoint.calc_linear_error(0,6,points_list)
        self.assertAlmostEqual(result,8.94427,5)
    def test_calc_error(self):
        # test to be run with LINEAR_COST_COEF = 1 
        # and ANGULAR_COST_COEF = 2
        spline = None
        waypoint = sda_path.SmoothWaypoint(spline)
        p1 = np.array([1,2,0])
        p2 = np.array([3,4,0])
        p3 = np.array([5,8,0])
        p4 = np.array([7,10,0])
        p5 = np.array([6,7,0])
        p6 = np.array([5,4,0])
        p7 = np.array([3,2,0])
        points_list = [p1,p2,p3,p4,p5,p6,p7]

        result = waypoint.calc_error(0,4,points_list)
        self.assertAlmostEqual(result,8.51818,4)

        result = waypoint.calc_error(3,6,points_list)
        self.assertAlmostEqual(result,1.537929,4)

        result = waypoint.calc_error(0,6,points_list)
        self.assertAlmostEqual(result,13.65665,4)


    def test_calc_error_between_all_point_pairs(self):
        # MUST BE THE SAME AS THE COST COEFFICIENST IN sda_path.py
        line_cost = 1
        angle_cost = 2
        spline = None
        waypoint = sda_path.SmoothWaypoint(spline)

        p1 = np.array([1,2,0])
        p2 = np.array([3,4,0])
        p3 = np.array([2,3,0])
        p4 = np.array([1,3,0])
        p5 = np.array([0,1,0])

        points_list = [p1,p2,p3,p4,p5]
        errors_matrix = waypoint.calc_error_between_all_point_pairs(points_list)

        result = errors_matrix[4][0]
        self.assertAlmostEquals(result,line_cost*2.82843 + angle_cost*0.321751,4)
        #calc error was tested before so it should be fine to use it to test this method
        result = errors_matrix[4][1]
        self.assertAlmostEquals(result,waypoint.calc_error(1,4,points_list))

        result = errors_matrix[4][2]
        self.assertAlmostEquals(result,waypoint.calc_error(2,4,points_list))

        result = errors_matrix[3][1]
        self.assertAlmostEquals(result,waypoint.calc_error(1,3,points_list))

        result = errors_matrix[2][1]
        self.assertAlmostEquals(result,waypoint.calc_error(1,2,points_list))

        result = errors_matrix[1][0]
        self.assertAlmostEquals(result,waypoint.calc_error(0,1,points_list))
    def test_to_points(self):
        point_1 = np.array([10,30])
        point_2 = np.array([20,40])
        point_3 = np.array([40,60])
        point_4 = np.array([40,15])
        waypoint = sda_path.SmoothWaypoint((point_1,point_2,point_3,point_4))
        time_step = 0.2
        # verified these results by inspection on a simulator
        result = str(waypoint.to_points(time_step))
        self.assertEquals(result, '[array([10, 30]), array([ 16.96,  36.6 ]), array([ 24.88,  42.  ]), array([ 32.32,  42.6 ]), array([ 37.84,  34.8 ]), array([ 40.,  15.])]')
    def test_generate_waypoints_from_smooth_curve(self):

        pass
    def test_calc_optimal_waypoint_path(self):
        spline = None
        waypoint = sda_path.SmoothWaypoint(spline)
        # treating spline_as_points_list as a list of ints for simplicoty
        # it should not matter for the sake of this test as the errors will
        # be given
        spline_as_points_list = [0,1,2,3,4,5,6,7,8,9,10]
        errors_matrix = [[],
                        [0],
                        [10,0],
                        [10,10,0],
                        [10,10,10,0],
                        [10,10,10,10,0],
                        [10,10,10,10,10,0],
                        [10,10,10,10,10,10,0],
                        [10,10,10,10,10,10,1,1],
                        [10,10,10,10,10,10,10,10,0],
                        [10,10,10,10,10,10,10,10,10,0]]
        result = waypoint.calc_optimal_waypoint_path(spline_as_points_list,errors_matrix)
        self.assertEquals(result,[0,1,2,3,4,5,6,8,9,10])

    def test_get_waypoints_from_opt_segments(self):
        spline = None
        waypoint = sda_path.SmoothWaypoint(spline)
        points =[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        # it should not matter that points is a list of ints
        # rather than points for this test
        opt_j_for_i = [-1,0,1,0,3,4,2,1,5,6,9,2,4,10,13]
        result = waypoint.get_waypoints_from_opt_segments(opt_j_for_i,points)
        self.assertEquals(result,[1,2,3,7,10,11,14,15])
    def test_smooth_path(self):
        k = 10
        path = sda_path.Path(k)
        point1 = np.array([10,209,132])
        point2 = np.array([700,10,175])
        point3 = np.array([12,79,35])
        path.smooth_path([point1,point2,point3])
        pass
    def test_transform_to_two_space(self):
        k = 10
        path = sda_path.Path(k)
        point1 = np.array([10,209,30])
        point2 = np.array([700,10,40])
        point3 = np.array([12,7,20])
        result = path.transform_to_two_space(point1,point2,point3)
        self.assertEquals(result[0][0],0)
        self.assertEquals(result[0][1],0)
        self.assertEquals(result[1][1],0)
    def test_transform_to_three_space(self):
        k = 10
        path = sda_path.Path(k)
        point1 = np.array([10,209,300])
        point2 = np.array([70,110,402])
        point3 = np.array([12,7,20])
        result = path.transform_to_two_space(point1,point2,point3)
        trans = result[3]

        new_result = path.transform_to_three_space(trans,result[0]) 
        self.assertAlmostEquals(new_result[0],point1[0])
        self.assertAlmostEquals(new_result[1],point1[1])
        self.assertAlmostEquals(new_result[2],point1[2])

        new_result = path.transform_to_three_space(trans,result[1])
        self.assertAlmostEquals(new_result[0],point2[0])
        self.assertAlmostEquals(new_result[1],point2[1])
        self.assertAlmostEquals(new_result[2],point2[2])

        new_result = path.transform_to_three_space(trans,result[2])
        self.assertAlmostEquals(new_result[0],point3[0])
        self.assertAlmostEquals(new_result[1],point3[1])
        self.assertAlmostEquals(new_result[2],point3[2])
    def test_smooth_waypoint_vertex(self):
        k = 10
        path = sda_path.Path(k)
        point1 = np.array([0,0])
        point2 = np.array([1,0])
        point3 = np.array([1,5])

        result = path.smooth_waypoint_vertex(point1,point2,point3)
        spline1 = result[0].getSpline()
        spline2 = result[1].getSpline()
        self.assertEquals(str(spline1),"(array([ 0.8412121,  0.       ]), array([ 0.87307766,  0.        ]), array([ 0.92801827,  0.        ]), array([ 0.96400437,  0.0359861 ]))")
        self.assertEquals(str(spline2),"(array([ 0.9640139 ,  0.03599563]), array([ 1.        ,  0.07198173]), array([ 1.        ,  0.12692234]), array([ 1.       ,  0.1587879]))")
        
if __name__ == '__main__':
    unittest.main()
