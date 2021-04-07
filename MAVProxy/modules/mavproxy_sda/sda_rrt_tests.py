import unittest
import numpy as np 
import modules.lib.mp_geometry as mp_geo
from sda_rrt import RRTree, RRTNode
import sda_pdriver

''' 
    Spec change: rrt first and second arguments of stationary and moving obstacles has been changed
                to a required argument of prob_model which contains both stationary and moving obstacles
'''

class SDARRTreeTests(unittest.TestCase):

    '''def test_nearest_neighbor(self):
        print "testing nearest neighbor..."
        pos0 = np.array([0, 0, 0])
        pos1 = np.array([1, 1, 1])
        pos2 = np.array([5, 5, 5])
        pos3 = np.array([-1, -1, -1])
        pos4 = np.array([50, 50, 50])
        heading = np.array([-100, 200, 80]) - np.array([100, 100, 80])

        pdriver = sda_pdriver.ProbDriver()
        pdriver.generate_model()

        test_tree = RRTree(pdriver.get_model(), None)
        test_tree_set = [RRTNode(pos0, heading), 
                            RRTNode(pos1, heading), 
                            RRTNode(pos2, heading), 
                            RRTNode(pos3, heading), 
                            RRTNode(pos4, heading)]
        
        test_pos1 = np.array([50, 50, 50])
        test_pos2 = np.array([2, 2, 2])
        test_pos3 = np.array([-50, -50, -50])

        test_1_result = test_tree.nearest_neighbor(test_pos1, test_tree_set, 1)
        test_2_result = test_tree.nearest_neighbor(test_pos2, test_tree_set, 1)
        test_3_result = test_tree.nearest_neighbor(test_pos3, test_tree_set, 1)

        self.assertEqual(test_1_result, test_tree_set[4])
        self.assertEqual(test_2_result, test_tree_set[1])
        self.assertEqual(test_3_result, test_tree_set[3])

    def test_path_causes_collision(self):
        print "testing path causes collision... "
        heading = np.array([-100, 200, 80]) - np.array([100, 100, 80])
        pos0 = RRTNode(np.array([100, 100, 80]), heading)
        pos1 = RRTNode(np.array([100, 200, 80]), heading)
        pos2 = RRTNode(np.array([200, 100, 80]), heading)
        pos3 = RRTNode(np.array([200, 200, 80]), heading)
        pos4 = RRTNode(np.array([-100, 200, 80]), heading)

        stat_pos = np.array([100, 150, 200])
        stat_obst = mp_geo.StationaryObstacle(20, stat_pos)

        geofence_points = [(0,0), (0, 400), (400, 400), (400, 0)]
        geofence = mp_geo.Geofence(geofence_points)

        pdriver = sda_pdriver.ProbDriver(geofence=geofence)
        pdriver.add_stat_obst(stat_obst)
        pdriver.generate_model()

        test_tree = RRTree(pdriver.get_model(), geofence)

        #self.assertTrue(test_tree.path_causes_collision(pos1, pos0))
        #self.assertTrue(test_tree.path_causes_collision(pos2, pos0))
        #self.assertTrue(test_tree.path_causes_collision(pos4, pos0))
        self.assertFalse(test_tree.path_causes_collision(pos3, pos2))

    def test_get_random_point(self):
        print "testing get random point..."
        heading = np.array([100, 200, 80]) - np.array([100, 100, 80])
        pos0 = RRTNode(np.array([100, 100, 80]), heading)
        pos1 = RRTNode(np.array([100, 200, 80]), heading)

        stat_pos = np.array([100, 150, 200])
        stat_obst = mp_geo.StationaryObstacle(20, stat_pos)

        geofence_points = [(0,0), (0, 400), (400, 400), (400, 0)]
        geofence = mp_geo.Geofence(geofence_points)

        pdriver = sda_pdriver.ProbDriver(geofence=geofence)
        pdriver.add_stat_obst(stat_obst)
        pdriver.generate_model()

        test_tree = RRTree(pdriver.get_model(), geofence)

        random_point = test_tree.get_random_point(pos0.position, pos1.position)
        center_point = np.array([200, 200, 80])

        self.assertFalse(geofence.crosses(mp_geo.Segment(random_point, center_point)))
        self.assertTrue(random_point[2] > 0)

    def test_generate_path_to_destination_no_collision(self):
        print "testing generate path to destination (no collision)..."
        pos0 = np.array([100, 100, 80])
        pos1 = np.array([100, 200, 80])
        pos2 = np.array([200, 100, 80])
        pos3 = np.array([200, 200, 80])
        pos4 = np.array([-100, 200, 80])

        goal_pos = np.array([300, 100, 90])
        goal = mp_geo.Waypoint(goal_pos[0], goal_pos[1], goal_pos[2])

        stat_pos = np.array([100, 150, 200])
        stat_obst = mp_geo.StationaryObstacle(20, stat_pos)

        geofence_points = [(0,0), (0, 400), (400, 400), (400, 0)]
        geofence = mp_geo.Geofence(geofence_points)
        center_point = np.array([200, 200, 80])

        pdriver = sda_pdriver.ProbDriver(geofence=geofence)
        pdriver.add_stat_obst(stat_obst)
        pdriver.generate_model()

        test_tree = RRTree(pdriver.get_model(), geofence)

        # no previous path, heading is towards goal
        path, path_changed, final_heading, final_time = test_tree.generate_path_to_destination(pos0, goal.dv, [], goal_pos - pos0, 0)

        self.assertFalse(mp_geo.Waypoint(pos0[0], pos0[1], pos0[2]) in path)
        self.assertFalse(goal in path)
        self.assertFalse(bool(path))
        self.assertFalse(path_changed)

        for point in path:
            self.assertFalse(geofence.crosses(mp_geo.Segment(point, center_point)))

        for wp1, wp2 in zip(path, path[1:]):
            self.assertFalse(test_tree.path_causes_collision(RRTNode(wp1.dv), RRTNode(wp2.dv)))

    def test_generate_path_to_destination_collision(self):
        print "testing generate path to destination (collision)..."
        pos0 = np.array([100, 100, 80])
        pos1 = np.array([100, 200, 80])
        pos2 = np.array([200, 100, 80])
        pos3 = np.array([200, 200, 80])
        pos4 = np.array([-100, 200, 80])

        goal_pos = np.array([300, 100, 90])
        goal = mp_geo.Waypoint(goal_pos[0], goal_pos[1], goal_pos[2])
        
        start = mp_geo.Waypoint(pos0[0], pos0[1], pos0[2])

        heading = goal.dv - start.dv

        stat_pos = np.array([150, 100, 200])
        stat_obst = mp_geo.StationaryObstacle(20, stat_pos)

        geofence_points = [(0,0), (0, 400), (400, 400), (400, 0)]
        geofence = mp_geo.Geofence(geofence_points)
        center_point = np.array([200, 200, 80])

        test_tree = RRTree([stat_obst], [], geofence)

        # no previous path, heading is towards goal
        path, path_changed, final_heading = test_tree.generate_path_to_destination(start.dv, goal.dv, [], heading, 0)

        self.assertFalse(start in path)
        self.assertFalse(goal in path)
        #self.assertTrue(bool(path))
        #self.assertTrue(path_changed)

        for point in path:
            self.assertFalse(geofence.crosses(mp_geo.Segment(point, center_point)))

        path_with_start_and_goal = [start] + path + [goal]
        for wp1, wp2 in zip(path_with_start_and_goal, path_with_start_and_goal[1:]):
            self.assertFalse(test_tree.path_causes_collision(RRTNode(wp1.dv, heading), RRTNode(wp2.dv, heading)))
    
    def test_generate_path_to_destination_collision_constrained(self):
        print "testing generate path to destination (collision, constrained)..."
        pos0 = np.array([100, 100, 80])
        pos1 = np.array([100, 200, 80])
        pos2 = np.array([200, 100, 80])
        pos3 = np.array([200, 200, 80])
        pos4 = np.array([-100, 200, 80])

        goal_pos = np.array([300, 100, 90])
        goal = mp_geo.Waypoint(goal_pos[0], goal_pos[1], goal_pos[2])
        
        start = mp_geo.Waypoint(pos0[0], pos0[1], pos0[2])

        heading = goal.dv - start.dv

        stat_pos = np.array([150, 100, 200])
        stat_obst = mp_geo.StationaryObstacle(20, stat_pos)

        geofence_points = [(0,0), (0, 400), (400, 400), (400, 0)]
        geofence = mp_geo.Geofence(geofence_points)
        center_point = np.array([200, 200, 80])

        test_tree = RRTree([stat_obst], [], geofence, constrain=True, min_turning_radius=10)

        # no previous path, heading is towards goal
        path, path_changed, final_heading = test_tree.generate_path_to_destination(start.dv, goal.dv, [], heading, 0)

        self.assertFalse(start in path)
        self.assertFalse(goal in path)
        #self.assertTrue(bool(path))
        #self.assertTrue(path_changed)

        for point in path:
            self.assertFalse(geofence.crosses(mp_geo.Segment(point, center_point)))

        path_with_start_and_goal = [start] + path + [goal]
        for wp1, wp2 in zip(path_with_start_and_goal, path_with_start_and_goal[1:]):
            self.assertFalse(test_tree.path_causes_collision(RRTNode(wp1.dv, heading), RRTNode(wp2.dv, heading)))

    def test_generate_path_to_destination_collision_constrained_heading(self):
        print "testing generate path to destination (collision, constrained, changed heading)..."
        pos0 = np.array([100, 100, 80])
        pos1 = np.array([100, 200, 80])
        pos2 = np.array([200, 100, 80])
        pos3 = np.array([200, 200, 80])
        pos4 = np.array([-100, 200, 80])

        goal_pos = np.array([300, 100, 90])
        goal = mp_geo.Waypoint(goal_pos[0], goal_pos[1], goal_pos[2])
        
        start = mp_geo.Waypoint(pos0[0], pos0[1], pos0[2])

        heading = np.array([0, 1, 0])

        stat_pos = np.array([150, 100, 200])
        stat_obst = mp_geo.StationaryObstacle(20, stat_pos)

        geofence_points = [(0,0), (0, 400), (400, 400), (400, 0)]
        geofence = mp_geo.Geofence(geofence_points)
        center_point = np.array([200, 200, 80])

        test_tree = RRTree([stat_obst], [], geofence, constrain=True, min_turning_radius=10)

        # no previous path, heading is towards goal
        path, path_changed, final_heading = test_tree.generate_path_to_destination(start.dv, goal.dv, [], heading, 0)

        self.assertFalse(start in path)
        self.assertFalse(goal in path)
        #self.assertTrue(bool(path))
        #self.assertTrue(path_changed)

        for point in path:
            self.assertFalse(geofence.crosses(mp_geo.Segment(point, center_point)))

        path_with_start_and_goal = [start] + path + [goal]
        for wp1, wp2 in zip(path_with_start_and_goal, path_with_start_and_goal[1:]):
            self.assertFalse(test_tree.path_causes_collision(RRTNode(wp1.dv, heading), RRTNode(wp2.dv, heading))) 

    def test_generate_path_to_destination_no_collision_constrained(self):
        print "testing generate path to destination (constrained)..."
        pos0 = np.array([100, 300, 80])
        pos1 = np.array([100, 200, 80])
        pos2 = np.array([200, 100, 80])
        pos3 = np.array([200, 200, 80])
        pos4 = np.array([-100, 200, 80])

        goal_pos = np.array([300, 100, 90])
        goal = mp_geo.Waypoint(goal_pos[0], goal_pos[1], goal_pos[2])
        
        start = mp_geo.Waypoint(pos0[0], pos0[1], pos0[2])

        heading = np.array([0, 1, 0])

        stat_pos = np.array([150, 100, 200])
        stat_obst = mp_geo.StationaryObstacle(20, stat_pos)

        geofence_points = [(0,0), (0, 400), (400, 400), (400, 0)]
        geofence = mp_geo.Geofence(geofence_points)
        center_point = np.array([200, 200, 80])

        test_tree = RRTree([stat_obst], [], geofence, constrain=True, min_turning_radius=10)

        # no previous path, heading is towards goal
        path, path_changed, final_heading = test_tree.generate_path_to_destination(start.dv, goal.dv, [], heading, 0)

        self.assertFalse(start in path)
        self.assertFalse(goal in path)
        self.assertFalse(bool(path))
        self.assertFalse(path_changed)

        for point in path:
            self.assertFalse(geofence.crosses(mp_geo.Segment(point, center_point)))

        path_with_start_and_goal = [start] + path + [goal]
        for wp1, wp2 in zip(path_with_start_and_goal, path_with_start_and_goal[1:]):
            self.assertFalse(test_tree.path_causes_collision(RRTNode(wp1.dv, heading), RRTNode(wp2.dv, heading))) 

    '''
    def test_generate_path_to_destination_constrained_stress_test(self):
        print "testing generate path to destination (constrained, stress test)..."
        pos0 = np.array([100, 100, 80])
        pos1 = np.array([100, 200, 80])
        pos2 = np.array([200, 100, 80])
        pos3 = np.array([200, 200, 80])
        pos4 = np.array([-100, 200, 80])

        goal_pos = np.array([350, 350, 90])
        goal = mp_geo.Waypoint(goal_pos[0], goal_pos[1], goal_pos[2])
        
        start = mp_geo.Waypoint(pos0[0], pos0[1], pos0[2])

        heading = np.array([0, 1, 0])

        stat_pos_1 = np.array([200, 100, 200])
        stat_obst_1 = mp_geo.StationaryObstacle(20, stat_pos_1)

        stat_pos_2 = np.array([150, 200, 200])
        stat_obst_2 = mp_geo.StationaryObstacle(60, stat_pos_2)

        stat_pos_3 = np.array([300, 300, 200])
        stat_obst_3 = mp_geo.StationaryObstacle(10, stat_pos_3)

        stat_pos_4 = np.array([320, 300, 200])
        stat_obst_4 = mp_geo.StationaryObstacle(10, stat_pos_4)

        stat_pos_5 = np.array([360, 300, 200])
        stat_obst_5 = mp_geo.StationaryObstacle(10, stat_pos_5)

        stat_pos_6 = np.array([300, 360, 200])
        stat_obst_6 = mp_geo.StationaryObstacle(20, stat_pos_6)

        stat_pos_7 = np.array([100, 360, 200])
        stat_obst_7 = mp_geo.StationaryObstacle(20, stat_pos_7)

        stat_pos_8 = np.array([350, 150, 200])
        stat_obst_8 = mp_geo.StationaryObstacle(60, stat_pos_8)

        stat_pos_9 = np.array([190, 320, 200])
        stat_obst_9 = mp_geo.StationaryObstacle(40, stat_pos_9)

        stat_pos_10 = np.array([260, 240, 200])
        stat_obst_10 = mp_geo.StationaryObstacle(30, stat_pos_10)

        stat_obsts = [stat_obst_1, stat_obst_2, stat_obst_3, stat_obst_4, stat_obst_5, stat_obst_6, stat_obst_7, stat_obst_8, stat_obst_9, stat_obst_10]

        geofence_points = [(0,0), (0, 400), (400, 400), (400, 0)]
        geofence = mp_geo.Geofence(geofence_points)
        center_point = np.array([200, 200, 80])

        model = sda_pdriver.ProbModelStatic()

        lst={"stationary":stat_obsts}
        eval_list=lst["stationary"]
        model.obstacles=eval_list
        model.geofences=geofence

        test_tree = RRTree(model, geofence, constrain=True, min_turning_radius=10)

        # no previous path, heading is towards goal
        path, path_changed, final_heading, time_stamp = test_tree.generate_path_to_destination(start.dv, goal.dv, [], heading, 0)

        self.assertFalse(start in path)
        self.assertFalse(goal in path)
        #self.assertTrue(bool(path))
        #self.assertTrue(path_changed)

        for point in path:
            self.assertFalse(geofence.crosses(mp_geo.Segment(point, center_point)))

        path_with_start_and_goal = [start] + path + [goal]
        for wp1, wp2 in zip(path_with_start_and_goal, path_with_start_and_goal[1:]):
            self.assertFalse(test_tree.path_causes_collision(RRTNode(wp1.dv, heading), RRTNode(wp2.dv, heading))) 
    '''
    # Tests for calc_max_turn_angle 
    def test_calc_max_turn_angle(self):
        print "testing calc max turn angle..."
        test_tree = RRTree([], [], None)
        min_turn_rad = 40 
        incr = 5
        max_turn_angle, max_t_a_heading = test_tree.calc_max_turn_angle(min_turn_rad, incr)
        
    def test_get_pos_and_heading(self):
        print "testing get pos and heading..."
        test_tree = RRTree([], [], None)
        min_turn_rad = 40 
        incr = 5
        max_turn_angle, max_t_a_heading = test_tree.calc_max_turn_angle(min_turn_rad, incr)

        p_i = np.array([0, 0, 0])
        h_i = np.array([0, 1, 0])

        # _ is h_f
        p_f, _ = test_tree.get_pos_and_heading(p_i[:2], h_i[:2], max_turn_angle, max_t_a_heading)

        self.assertTrue(np.linalg.norm(p_f - np.array([0.3125, 4.99022482])) < mp_geo.EPSILON)

    def test_constrain_movement_towards_point(self):
        print "testing constrain movement towards point..."
        nn_point = np.array([100, 100, 80])
        heading_point = np.array([100,200, 80])
        rand_point = np.array([200, 100, 80])

        nn = [RRTNode(nn_point, heading_point - nn_point)]

        test_tree = RRTree([], [], None, min_turning_radius=50)
        new_nodes, extra = test_tree.constrain_movement_towards_point(rand_point, nn, nn[0])
        print "new nodes", new_nodes
        self.assertTrue(new_nodes[-1].is_angled_towards(rand_point))
    def test_time_stamps(self):
        print "testing time stamps"
        start_pos = np.array([0,0,0])
        start_time_stamp = 0
        start_heading = np.array([1,0,0])

        goal = np.array([150,50,0])

        test_tree = RRTree([],[],None,constrain=True,min_turning_radius=50)

        start_node = RRTNode(start_pos,start_heading,start_time_stamp)

        last_added_node = start_node

        new_nodes = test_tree.generate_path_to_destination(start_pos, goal, [], start_heading, 10)
        print new_nodes

    def test_prob_model_collisions(self):
        print "Testing prob model collisions"
        #heading is irrelevant for these tests
        heading = np.array([1,0,0])
        pos_1 = np.array([100,100,100])
        node_1 = RRTNode(pos_1, heading, time_stamp=0)

        pos_2 = np.array([100,105,100])
        node_2 = RRTNode(pos_2, heading, time_stamp=0)

        pos_3 = np.array([500,100,100])
        node_3 = RRTNode(pos_3, heading, time_stamp=0)

        pos_4 = np.array([100,100,100])
        node_4 = RRTNode(pos_4, heading, time_stamp=0)

        pos_5 = np.array([100,110,100])
        node_5 = RRTNode(pos_5, heading, time_stamp=0)

        obstacles = {"stationary": []}

        prob_model = sda_pdriver.ProbModelLinearInterp()
        #prob_model.generate(obstacles)

        test_tree = RRTree([],None,prob_model=prob_model)

        #print test_tree.path_causes_collision(node_4, node_1)
        #print test_tree.path_causes_collision(node_3,node_4)
        #print test_tree.path_causes_collision(node_4, node_1)'''

if __name__ == '__main__':
    unittest.main()
    
