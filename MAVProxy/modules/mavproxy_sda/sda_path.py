import modules.lib.mp_geometry as mp_geo
import math
import numpy as np
from collections import namedtuple

Transformation = namedtuple("Transformation",["two_space","z","translation","rotation"])
class SmoothWaypoint:

    LINE_COST = 2.8# cost associated with adding a new line
    LINEAR_COST_COEF = 2 # determines weight placed on linear error
    ANGULAR_COST_COEF = 50 # determines weight placed on angular error

    def __init__(self, spline):
        self.spline = spline
    def getSpline(self):
        # returns the actual spline not a copy
        # should only be used for testing
        return self.spline

    def generate_waypoints_from_smooth_curve(self,time_step):
        spline_as_points_list = self.to_points(time_step)
        errors_matrix = self.calc_error_between_all_point_pairs(spline_as_points_list)
        # converting the optimum array into a set of points
        return self.calc_optimal_waypoint_path(spline_as_points_list, errors_matrix)

    def calc_error_between_all_point_pairs(self, spline_as_points_list):
        errors_matrix = [None] * len(spline_as_points_list) 
        # get indecies in reversed order
        for i in reversed(xrange(len(spline_as_points_list))):
            errors_for_i = []
            for j in range(i):
                errors_for_i.append(self.calc_error(j, i, spline_as_points_list))
            errors_matrix[i] = errors_for_i 
        return errors_matrix

    def calc_optimal_waypoint_path(self, spline_as_points_list, errors_matrix):
        # the array containing minimum errors
        opt = [0] 
        # the array containing the start of the line segment that minimizes error
        opt_j_for_i = [-1]
        for i in xrange(len(spline_as_points_list)):
            for j in xrange(i):
                #initializing optimum
                if j == 0: 
                    opt.append(errors_matrix[i][j] + SmoothWaypoint.LINE_COST)
                    opt_j_for_i.append(0)
                # the main reccurence
                elif errors_matrix[i][j] + SmoothWaypoint.LINE_COST + opt[j - 1] < opt[i]:
                    opt[i] = errors_matrix[i][j] + SmoothWaypoint.LINE_COST + opt[j - 1]
                    opt_j_for_i[i] = j
        return self.get_waypoints_from_opt_segments(opt_j_for_i, spline_as_points_list)

    def get_waypoints_from_opt_segments(self, opt_j_for_i, points):
        waypoint_path = [points[-1]]
        i = len(points) - 1
        while(i > 0):
            waypoint_path.append(points[opt_j_for_i[i]])
            i = opt_j_for_i[i]
        # reverse the list and then remove the first and last point
        return waypoint_path[::-1][1:-1]

    def calc_error(self, i_1, i_2, points):
        linear_error = SmoothWaypoint.LINEAR_COST_COEF*self.calc_linear_error(i_1, i_2, points)
        angular_error = SmoothWaypoint.ANGULAR_COST_COEF*self.calc_angular_error(i_1,i_2, points)
        return angular_error + linear_error

    def calc_linear_error(self, i_1, i_2, points):
        chord = mp_geo.Segment(points[i_1], points[i_2])
        if i_2 - i_1 < 3:
            return 0
        
        start_index = i_1
        end_index = i_2
        while(start_index < end_index):
            my_range = end_index - start_index
            search_index = my_range/2 + start_index
            dist_to_point = chord.distance(mp_geo.Point(np_array=points[search_index]))
            if search_index > 0 and dist_to_point <= chord.distance(mp_geo.Point(points[search_index - 1])):
                # we get further from the line by reversing on the curve
                end_index = search_index
            elif search_index < len(points) - 1 and dist_to_point <= chord.distance(mp_geo.Point(points[search_index + 1])):
                # we get further fromt he line by progressing on the curve
                start_index = search_index + 1 
            else:
                return dist_to_point
        return dist_to_point

    # a better but more complicated version of linear error calculation
    #def calc_linear_error(self, index_point_1, index_point_2, spline_as_points_list):
        # possibly change later
        # will compute the maximum distance from the bezier curve to the line
        # to do this we determine when the derivative of the bezier curve
        # is parallel to the vector between point 1 and 2
        # using projections with this point we can determine 
        # the maximum distance from the line to the curve 
            #v = spline_as_points_list[index_point_2] - spline_as_points_list[index_point_1]
        # the control points along the spline
            #p_1 = self.spline_1[0]
            #p_2 = self.spline_1[1]
            #p_3 = self.spline_1[2]
            #p_4 = self.spline_1[3]
        # the vectors between progressive parts of points,
        # needed to calculate the derivative of the bezier curve
            #v_1 = p_2 - p_1
            #v_2 = p_3 - p_2
            #v_3 = p_4 - p_3
        # equation for the derivative of the Bezier Curve
        # 3t^2(v_1 + 2v_2 + v_3) + 6t(-v_1 + v_2) + 3v_1
        # equation we get to establish parallel
        # Cv = 3t^2(v_1 + 2v_2 + v_3) + 6t(-v_1 + v_2) + 3v_1
        # decompose them component-wise to get 2 equations
        # create constants to make solving system of equations simpler
            #x_quad = p_1.x + 2*p_2.x + p_3.x
            #y_quad = p_1.y + 2*p_2.y + p_3.y
            #x_lin = -p_1.x + p_2.y 
            #y_lin = -p_1.x + p_2.y 
        # when C is solved for and substitution is used we are left with
        # the following constants for a quadratic equation:
            #a = 3 * y_quad - 3 * x_quad * (v.y/v.x)
            #b = 6 * y_lin - 6 * x_lin * (v.y/v.x)
            #c = 3 * p_2.y - 3 * p_2.x * (v.y/v.x)
        # the time in which the derivative is parallel to v
        # check this (second equation !?!?!) 
            #t = (b + math.sqrt(b**2 - 4*a*c))/(2*a)

    def calc_angular_error(self, i_1, i_2, points):
        chord = points[i_2] - points[i_1]
        approx_deriv = points[i_2] - points[i_2 - 1]
        #angle between two vectors using dot product
        num = chord.dot(approx_deriv)
        denom = (np.linalg.norm(chord)*np.linalg.norm(approx_deriv))
        value = num/denom
        if value > 1:
            value = 1
        if value < -1:
            value = -1
        angular_error = math.acos(value)
        return angular_error

    def to_points(self,time_step): #returns a set of points from the bezier curve
        t = 0
        spline_as_points_list = []
        # bezier curves are defined from t 0 to 1
        while t <= 1:
            control_pnt_1_weight = ((1-t)**3)*self.spline[0] 
            control_pnt_2_weight = 3*((1-t)**2)*t*self.spline[1] 
            control_pnt_3_weight = 3*(1-t)*t**2*self.spline[2]
            control_pnt_4_weight = (t**3)*self.spline[3]
            current_point = control_pnt_1_weight + control_pnt_2_weight + control_pnt_3_weight + control_pnt_4_weight
            #setting z-axis of all points to be 0
            spline_as_points_list.append(current_point)
            t += time_step
        return spline_as_points_list

class Path:

    def __init__(self, k_max):
        self.k_max = k_max

    # TODO: TEST
    def smooth_path(self, waypoints):
        smoothed_path = []
        for wp1, wp2, wp3 in zip(waypoints, waypoints[1:], waypoints[2:]):   

            wp1_2d, wp2_2d, wp3_2d, matrix_info= self.transform_to_two_space(wp1.dv, wp2.dv, wp3.dv)

            control_points = self.smooth_waypoint_vertex(wp1_2d, wp2_2d, wp3_2d)
            curved_wp_a = control_points[0]
            curved_wp_b = control_points[1]

            smoothed_path_2d = curved_wp_a.generate_waypoints_from_smooth_curve(.1)
            smoothed_path_2d += curved_wp_b.generate_waypoints_from_smooth_curve(.1)
            for wp_2d in smoothed_path_2d:
                # transform back to three space
                wp_3d = self.transform_to_three_space(matrix_info,wp_2d)
                smoothed_path.append(mp_geo.Waypoint(wp_3d[0], wp_3d[1], wp_3d[2], sda=True))
        return smoothed_path
        #TODO: Make not shit
    def transform_to_two_space(self,wp1, wp2, wp3):
        u_x = (wp2 - wp1) / np.linalg.norm(wp2 - wp1)
        u_y_prime = (wp3 - wp2) / np.linalg.norm(wp3 - wp2)
        u_z = np.cross(u_x,u_y_prime) / np.linalg.norm(np.cross(u_x,u_y_prime))
        u_y = np.cross(u_z,u_x)
        TM = np.matrix([[u_x[0],u_y[0],u_z[0]],
                        [u_x[1],u_y[1],u_z[1]],
                        [u_x[2],u_y[2],u_z[2]]])

        point1 = np.column_stack((wp1,))
        point2 = np.column_stack((wp2,))
        point3 = np.column_stack((wp3,))
        #waypoints with equal z_cordinates
        wp1_3d = np.dot(TM.getI(), point1)
        wp2_3d = np.dot(TM.getI(), point2)
        wp3_3d = np.dot(TM.getI(), point3)

        z_cord = wp1_3d[2,0]

        wp1_2d = np.array([wp1_3d[0,0],wp1_3d[1,0]])
        wp2_2d = np.array([wp2_3d[0,0],wp2_3d[1,0]])
        wp3_2d = np.array([wp3_3d[0,0],wp3_3d[1,0]])

        translation_array = np.array([-wp1_2d[0],-wp1_2d[1]])
        wp1_2d = wp1_2d + translation_array
        wp2_2d = wp2_2d + translation_array
        wp3_2d = wp3_2d + translation_array

        v2 = (wp2_2d - wp1_2d)
        angle = math.atan(v2[1]/v2[0])
        rotation_M = np.matrix([[math.cos(angle), -math.sin(angle)],
                              [math.sin(angle) , math.cos(angle)]])
        wp1_rotated = np.array(np.dot(rotation_M,wp1_2d))
        wp2_rotated = np.array(np.dot(rotation_M,wp2_2d))
        wp3_rotated = np.array(np.dot(rotation_M,wp3_2d))

         
        trans = Transformation(TM,z_cord,translation_array,rotation_M)

        wp1_final = np.array([wp1_rotated[0,0],wp1_rotated[0,1]])
        wp2_final = np.array([wp2_rotated[0,0],wp2_rotated[0,1]])
        wp3_final = np.array([wp3_rotated[0,0],wp3_rotated[0,1]])
        return wp1_final, wp2_final, wp3_final,trans 

    def transform_to_three_space(self,trans,wp):
        wp_2d_vert = np.column_stack((wp,))

        waypoint = np.dot(trans.rotation.getI(),wp_2d_vert)

        waypoint = np.array([waypoint[0,0],waypoint[1,0]])
        waypoint = waypoint - trans.translation
        waypoint = np.array([waypoint[0],waypoint[1],trans.z])
        waypoint = np.dot(trans.two_space,waypoint)
        waypoint = np.array([waypoint[0,0],waypoint[0,1],waypoint[0,2]])
        return waypoint
    # TODO: fuck if i know how to test this
    def smooth_waypoint_vertex(self, P1, P2, P3):

        v_1 = (P1-P2)
        v_2 = (P3-P2)
        u_1 = v_1 / np.linalg.norm(v_1)
        # because fuck yang and sukkarieha 
        u_2 = -1*(v_2 / np.linalg.norm(v_2))

        # law of cosines used to find the interior angle between P1, P2, and P3 with P2 as the vertex 
        # We then found the exterior angle by subtracting it from pi
        gamma = math.pi - math.acos(v_1.dot(v_2)/(np.linalg.norm(v_1) * np.linalg.norm(v_2)))
        beta = gamma/2
        d = 1.1228 * math.sin(beta)/(self.k_max * math.cos(beta)**2)

        h_b = 0.346*d
        g_b = 0.58 * h_b
        k_b = 1.31 * h_b * math.cos(beta)
        
        h_e = h_b
        g_e = 0.58 * h_b
        k_e = 1.31 * h_b * math.cos(beta)

        B_0 = P2 + d * u_1
        B_1 = B_0 - g_b * u_1
        B_2 = B_1 - h_b * u_1

        E_3 = P2 - d * u_2
        E_2 = E_3 + g_e * u_2
        E_1 = E_2 + h_e * u_2

        v_d = E_3 - B_0
        u_d = v_d / np.linalg.norm(v_d)

        B_3 = B_2 + k_b * u_d
        E_0 = E_1 - k_e * u_d

        return (SmoothWaypoint((B_0, B_1, B_2, B_3)),SmoothWaypoint((E_0, E_1, E_2, E_3)))

