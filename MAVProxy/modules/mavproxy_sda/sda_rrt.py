import random
import sys
import time
import os
import math
import traceback
import modules.lib.mp_geometry as mp_geo
from itertools import chain, combinations
from scipy import spatial
import numpy as np 
import mavproxy_logging
import modules.mavproxy_sda.sda_pdriver

#logger = mavproxy_logging.create_logger("sda rrt")

def powerset(iterable):
    """
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    xs = list(iterable)
    # note we return an iterator rather than a list
    return chain.from_iterable(combinations(xs,n) for n in range(len(xs)+1))

class RRTNode:
    def __init__(self, position, heading, time_stamp=0):
        # 3-D RRT
        assert(len(position) == 3)
        self.position = position
        self.parent = None
        self.time_stamp = time_stamp
        self.children = []
        self.heading = mp_geo.unit_vector(heading)
        self.pinned = False
    
    def set_time_stamp(self, t=None, speed=None, prev_time_stamp=None, distance=None):
        if t != None: 
            self.time_stamp = t
        elif speed != None:
            if distance == None:
                assert self.parent != None, "Parent node is none so we can't generate a distance to compute a timestamp"
                distance = self.get_distance(self.parent)
            if prev_time_stamp == None:
                assert self.parent != None, "Parent node is none so we can't generate a timestamp"
                prev_time_stamp = self.parent.time_stamp
            if speed != 0:
                self.time_stamp = prev_time_stamp + (distance / speed)
            else: 
                self.time_stamp = prev_time_stamp + 100000

    def add_child(self, child):
        self.children.append(child)

    def set_parent(self, parent):
        self.parent = parent

    # angles are only computed on the x, y axis
    def is_angled_towards(self, point, return_angle=False):
        num_degrees = 4
        dir_vec_xy = mp_geo.unit_vector(point[:2] - self.position[:2])
        heading_xy = mp_geo.unit_vector(self.heading[:2])

        #min used to prevent acos domain errors due to floating imprecision
        dot_product_xy = heading_xy.dot(dir_vec_xy)
        angle = abs(math.acos(np.clip(dot_product_xy, -1, 1)))
        angle = math.degrees(angle)

        is_pointed = angle < num_degrees
        if return_angle:
            return is_pointed, angle
        return is_pointed

    #returns the distance between two nodes
    def get_distance(self, node2):
        return np.linalg.norm(self.position - node2.position)

    def __getitem__(self, key): 
        return self.position.__getitem__(key)

    def __repr__(self):
        return 'RRTNode(position=np.array(' + str([x for x in self.position]) + ') , heading=np.array(' + str([x for x in self.heading]) + ') , time_stamp=' + str(self.time_stamp) + ')'

class RRTree:

    class ConstraintViolationException(Exception):
        pass

    # probability that the tree will bias itself towards the goal point, 0.01
    GOAL_PROB = 0.1
    # probability that the tree will bias towards points that were present in the last calculation of the tree
    HISTORY_PROB = 0.02

    def __init__(self, prob_model, geofence, increment=5, constrain=True, min_turning_radius=50, timeout=5, prob_threshold=0.9, collision_increment=5):
        self.geofence = geofence
        # the rate at which the tree moves forward defaults to 5 meters
        self.increment = increment
        self.constrain = constrain
        self.timeout = timeout 
        self.max_turn_angle, self.max_turn_heading = self.calc_max_turn_angle(min_turning_radius, increment)
        self.prob_model = prob_model   
        self.prob_threshold = prob_threshold
        self.collision_increment = collision_increment
        self.speed = 1
    
    # Returns the speed of the plain at time t
    def get_speed(self):
        return self.speed

    # Returns maximum angle between a straight flying plane and min turning radius plane at distance increment
    # from initial position. Also caculates the angle between the two headings  
    # 
    # @param    min_turning_radius: number in meters
    # @param    increment: number in meters
    #
    # @returns  max_turn_angle: float in radians
    # @returns  max_turn_heading: float in radians
    def calc_max_turn_angle(self, min_turning_radius, increment):
        max_turn_angle = math.pi/2 - math.acos((increment/2.0)/min_turning_radius)
        radius_intersect = np.array([increment * math.sin(max_turn_angle), increment * math.cos(max_turn_angle), 0])
        heading_slope = (min_turning_radius - radius_intersect[0]) / radius_intersect[1]
        heading_vec = np.array([1, heading_slope, 0])
        max_t_a_heading = math.acos( mp_geo.unit_vector(heading_vec).dot(np.array([0,1,0])) )
        return max_turn_angle, max_t_a_heading

    # Returns all additional waypoints that must be added to the path between 
    # [start_pos] and [goal] to create a collisionless path. 
    # Returns [] if no additional waypoints must be placed 
    # 
    # @param    start_pos: np.array([x, y, z])
    # @param    goal: np.array([x, y, z])
    # @param    prev_path: [[x, y, z], [x, y, z], ...]
    # @param    init_heading: np.array([x, y, z])
    #
    # @returns  pruned_path: [Waypoint(x, y, z) , Waypoint(x, y, z), ...]
    # @returns  path_changed: boolean
    def generate_path_to_destination(self, start_pos, goal, prev_path, init_heading, init_time_stamp):
        collision = False
        # if list is not empty
        if prev_path:

            prev_path_to_waypoint = [mp_geo.Waypoint(*tuple(start_pos))] + prev_path + [mp_geo.Waypoint(*tuple(goal))]
            collision, final_node = self.simulate_path_through_waypoints(prev_path_to_waypoint, init_heading)
            self.log_waypoints(prev_path_to_waypoint, 'waypoints.debug', collision)
            if not collision:
                return prev_path, False, final_node.heading, final_node.time_stamp
        
        # create node for start position
        start_node = RRTNode(start_pos, init_heading, init_time_stamp)
        
        # init stands for inital trial, meaning its the first loop through the the while loop
        # On the initial trial, we want to try to go directly towards the goal. If that doesn't work 
        # we continue on with the normal algorithm
        init = True
        
        # will be assigned at the end
        goal_node = None
        
        # for generating the KDTree and other things that require all nodes
        tree = [start_node]
        found_goal = False
        last_added_node = tree[0]

        timeout_timer_start_time = time.time()

        while(not found_goal and time.time() - timeout_timer_start_time < self.timeout):
            # get a list of new nodes to add and the node the list should attach to
            try: 
                new_node_set, nearest_tree_node = self.extend_tree(tree, last_added_node, goal, prev_path, init)
            except RRTree.ConstraintViolationException as e:
                continue
            finally:
                init=False

            # If the list is empty that means we couldn't extend the tree however the extension algorithm was trying to do
            # Therefore, we just run extend tree again until it works
            if not new_node_set and nearest_tree_node is not None: 
                last_added_node = nearest_tree_node
                continue

            # linking the new nodes to the tree
            nearest_tree_node.add_child(new_node_set[0])
            new_node_set[0].set_parent(nearest_tree_node)
            last_added_node = new_node_set[-1]
            tree += new_node_set

            # checks to see if we have found goal
            found_goal = np.linalg.norm(last_added_node.position - goal) < self.increment
            if found_goal:
                # the heading on the goal node shouldn't matter... i think?
                goal_node = RRTNode(goal, last_added_node.heading, time_stamp=last_added_node.time_stamp)
                goal_node.set_parent(last_added_node)
                tree.append(goal_node)

        if time.time() - timeout_timer_start_time >= self.timeout:
            self.write_tree(tree, 'tree.debug', goal, timeout=True)
            print("RRT timed out")
            return [], False, None, None
        self.write_tree(tree, 'tree_success.debug', goal)

        # get the full branch of the tree that found the goal
        path = self.get_path_from_tree(goal_node, start_pos)
        # prune the path to minimize waypoints
        self.write_tree(path, 'path_n.debug', goal)

        pruned_path = self.prune_and_convert_to_waypoints(path)
        #self.write_tree(pruned_path, 'path.debug', goal)
        #self.write_path(pruned_path, 'debug.pruned')

        # Uses truthiness of pruned path. Empty list means path need not be updated
        return pruned_path, bool(pruned_path), goal_node.heading, goal_node.time_stamp
        



    # Returns a list of waypoints that create a valid path from a node on the tree 
    # Returns [] if randomized algorithm cannot extend tree in random manner
    # chosen. In this case, run this function again
    # 
    # @param    tree: [RRTNode, RRTNode, RRTNode, ..., RRTNode]
    # @param    last_added_node: RRTNode
    # @param    goal: np.array([x, y, z])
    # @param    prev_path: [Waypoint(x, y, z), Waypoint(x, y, z), ..., Waypoint(x, y, z)]
    # @param    init: boolean 
    #
    # @returns  new_nodes: [RRTNode, RRTNode, RRTNode, ..., RRTNode]
    # @returns  tree_node: RRTNode to which you attach new nodes
    #TODO KNOWN BUG init=true ignores heading
    def extend_tree(self, tree, last_added_node, goal, prev_path, init):
        
        # probability: (0, 1)
        prob = random.random()
        # create a new node that extends the line that the previous node made, with its heading
        new_point = last_added_node.position + (last_added_node.heading*self.increment)
        new_node = RRTNode(new_point, last_added_node.heading)
        new_node.set_parent(last_added_node)
        new_node.set_time_stamp(speed=self.get_speed(), prev_time_stamp=last_added_node.time_stamp)

        # if we don't turn towards the goal and we don't collide with anything then just return that node and keep going
        if prob >= RRTree.GOAL_PROB and not self.path_causes_collision(new_node, last_added_node) and not init:
            return [new_node], last_added_node

        # determine what the random point is
        if prob < RRTree.GOAL_PROB or init:
            random_point = goal
            if not self.constrain:
                direction_vec = mp_geo.unit_vector(random_point-last_added_node.position)
                new_point = last_added_node.position + (direction_vec*self.increment)
                new_node = RRTNode(new_point, direction_vec)
                new_node.set_parent(last_added_node)
                new_node.set_time_stamp(speed=self.get_speed(), prev_time_stamp=last_added_node.time_stamp)
                if not self.path_causes_collision(new_node, last_added_node):
                    return [new_node], last_added_node

        elif len(prev_path) > 0 and prob < self.GOAL_PROB + self.HISTORY_PROB:
            random_point = random.choice(prev_path).dv
        else: 
            random_point = self.get_random_point(last_added_node.position, goal)

        # get nearest node on tree to random point
        nearest_neighbors = self.nearest_neighbor(random_point, tree, 10)
        nn = nearest_neighbors[0]
        new_nodes = []

        # determine what the new node(s) is/are to extend 
        if self.constrain and not last_added_node.is_angled_towards(random_point):
            # if we want to constrain the RRT build up a list of nodes that meet the curvature constraint
            new_nodes, tree_node = self.constrain_movement_towards_point(random_point, nearest_neighbors, last_added_node)
            nn = tree_node
            nn.pinned = True
        elif last_added_node.is_angled_towards(random_point): 
            return [], last_added_node
        # otherwise constrain is turned off
        else: 
            # else add a new node in the direction of the random point but self.increment distance away from the nn node
            direction_vec = mp_geo.unit_vector(random_point-nn.position)
            new_point = nn.position + (direction_vec*self.increment)
            new_node = RRTNode(new_point, direction_vec)

            # Make sure we're not adding nodes that cause collisons 
            while self.path_causes_collision(new_node, nn):
                random_point = self.get_random_point(last_added_node.position, goal)
                nn = self.nearest_neighbor(random_point, tree, 1)

                direction_vec = mp_geo.unit_vector(random_point-nn.position)
                new_point = nn.position + (direction_vec*self.increment)
                new_node = RRTNode(new_point, direction_vec)
            new_node.set_parent(nn)
            new_node.set_time_stamp(speed=self.get_speed(), prev_time_stamp=nn.time_stamp)
            new_nodes.append(new_node)
        return new_nodes, nn

    # Returns a list of waypoints that turn the heading of the plane towards a desired
    # point in space given the curvature constraints of the plane 
    # Returns [] if this is not possible from any of the points
    # from the tree that were input
    # 
    # @param    point: np.array([x, y, z])
    # @param    nearest_nodes: [RRTNode, RRTNode, RRTNode, ..., RRTNode]
    # @param    last_added_node: RRTNode
    #
    # @returns  new_nodes: [RRTNode, RRTNode, RRTNode, ..., RRTNode]
    # @returns  tree_node: RRTNode to which you attach new nodes
    def constrain_movement_towards_point(self, point, nearest_nodes, last_added_node, max_iterations=200):
    
        '''with open('rrt.log', 'a') as f:
            my_str = 'point, lst, node = np.array(' + str([x for x in point]) + '), ' + str(nearest_nodes) + ', ' + str(last_added_node) + '\n'
            my_str += 'points.append(point)\nnns.append(lst)\nlast_added_nodes.append(node)\n'
            f.write(my_str)'''

        nodes_to_check = [last_added_node] + nearest_nodes
        for tree_node in nodes_to_check:
            new_nodes = []
            curr_leaf_node = tree_node
            no_collisions = True
            i = 0
            # while the plane is not angled towards the point or within range of the point it is trying to turn towards
            while no_collisions and not curr_leaf_node.is_angled_towards(point) and not np.linalg.norm(point - curr_leaf_node.position) < self.increment and i < max_iterations:
                i += 1
                scaled_random_vec = mp_geo.unit_vector(point - curr_leaf_node.position) * self.increment
                scaled_random_point = curr_leaf_node.position + scaled_random_vec
                scaled_rand_z = scaled_random_point[2]
                # signed angle between nearest_nodes heading and random point
                theta = math.atan2(curr_leaf_node.heading[1], curr_leaf_node.heading[0]) - math.atan2(scaled_random_vec[1], scaled_random_vec[0])
                # ensure thetea is between -pi and pi
                theta = self.wrap_min_max(theta)
                if abs(theta) > self.max_turn_angle: 
                    # comp(theta, 0) gets the sign of theta    
                    theta = cmp(theta, 0) * self.max_turn_angle
                adjusted_xy, adjusted_heading_xy = self.compute_pos_and_heading_from_theta(curr_leaf_node.position[:2], curr_leaf_node.heading[:2], theta)
                # create a 3D point from z and the adjusted xy
                adjusted_xyz = np.append(adjusted_xy, [scaled_rand_z])
                adjusted_heading_xyz = np.array([adjusted_heading_xy[0], adjusted_heading_xy[1], curr_leaf_node.heading[2]])
                
                # determine node to extend from
                if len(new_nodes) == 0:
                    extend_node = tree_node
                else:
                    extend_node = new_nodes[-1]
                
                # instantiate a new node    
                new_node = RRTNode(adjusted_xyz, adjusted_heading_xyz)
                if new_node.is_angled_towards(point):
                    new_node.heading = mp_geo.unit_vector(point-new_node.position) 

                dist = curr_leaf_node.get_distance(new_node)
                # update the time of the new node
                new_node.set_time_stamp(speed=self.get_speed(), prev_time_stamp=curr_leaf_node.time_stamp, distance=dist)
                
                # make sure adding this will not cause a collision
                if self.path_causes_collision(new_node, curr_leaf_node):
                    no_collisions = False
                else:
                    curr_leaf_node = new_node
                    new_nodes.append(curr_leaf_node)

            if i == max_iterations:
                no_collisions = False

            # if there is a collision go to next tree node to start from
            if no_collisions: 
                # otherwise connect the nodes and return them 
                if len(new_nodes) > 1:
                    for n1, n2 in zip(new_nodes, new_nodes[1:]): 
                        n1.add_child(n2)
                        n2.set_parent(n1)
                return new_nodes, tree_node
       
        raise RRTree.ConstraintViolationException()

    def wrap_max(self, x, max_val):

        # integer math: `(max + x % max) % max` 
        return (max_val + x % max_val) % max_val


    # constrains theta to within -pi and pi 
    # 
    # @param    theta: float in radians 
    #
    # @returns  theta: float in radians
    def wrap_min_max(self, x, min_val= -math.pi, max_val=math.pi):
        return min_val + self.wrap_max(x - min_val, max_val - min_val)


    # calculates the correct position and heading for the plane when it turns at angle
    # [theta] after [self.increment] meters 
    # 
    # @param    p_i: np.array([x, y, z])
    # @param    h_i: np.array([x, y, z])
    # @param    theta: float in radians 
    #
    # @return   p_f: np.array([x, y, z])
    # @return   h_f: np.array([x, y, z]) 
    def compute_pos_and_heading_from_theta(self, p_i, h_i, theta):
        x = (theta + self.max_turn_angle) / (2 * self.max_turn_angle) 
        heading_theta =  -1 * self.max_turn_heading + x * 2 * self.max_turn_heading

        return self.get_pos_and_heading(p_i, h_i, theta, heading_theta)

    # Applies the matricies for determining the correct position and heading
    # 
    # @param    p_i: np.array([x, y, z])
    # @param    h_i: np.array([x, y, z])
    # @param    theta_1: float in radians 
    # @param    theta_2: float in radians
    #
    # @return   p_f: np.array([x, y, z])
    # @return   h_f: np.array([x, y, z]) 
    def get_pos_and_heading(self, p_i, h_i, theta_1, theta_2):
        h_to_f = np.mat(h_i) * np.matrix([
            [math.cos(theta_1), -math.sin(theta_1)],
            [math.sin(theta_1), math.cos(theta_1)]
            ]) 
        h_f = np.mat(h_i) * np.matrix([
            [math.cos(theta_2), -math.sin(theta_2)],
            [math.sin(theta_2), math.cos(theta_2)]
            ]) 
        return np.squeeze(np.asarray(p_i + self.increment * h_to_f)), np.squeeze(np.asarray(h_f))

    # Returns a random point from within the geofence. z coordinate will be now greater than 
    # max(start_pos.z, goal.z) and no less than min(start_pos.z, goal.z)
    # 
    # @param    start_pos: np.array([x, y, z])
    # @param    goal: np.array([x, y, z])
    #
    # @return   random_point: np.array([x, y, z])
    def get_random_point(self, start_pos, goal):
        if self.geofence != None:
            rand_xy = self.geofence.sample_random_point()
        else:
            # for testing
            rand_xy = (start_pos[0] + random.uniform(-10000, 10000), start_pos[1] + random.uniform(-10000, 10000))

        path = mp_geo.Segment(start_pos, goal)
        # z coord is zero because it doesn't matter
        rand_point = mp_geo.Point(x=rand_xy[0], y=rand_xy[1], z=0)
        proj = path.projection(rand_point)
        return np.array([rand_point.x, rand_point.y, proj[2]])
        
    # Converts a list of RRTNodes to a list of sda=True Waypoint objects 
    # 
    # @param    path: [RRTNode, RRTNode, ..., RRTNode]
    #
    # @return   waypoints: [Waypoint, Waypoint, ..., Waypoint]
    def to_waypoints(self, path):
        waypoints = []
        for node in path:
            x = node.position[0]
            y = node.position[1]
            z = node.position[2]
            waypoints.append(mp_geo.Waypoint(x, y, z, sda=True))
        return waypoints

    # removes unnecessary waypoints from path. 
    # 
    # Implementation Notes: Start position and goal position nodes
    # are passed in as the first and last nodes respectively. These are trimmed once the 
    # algorithm is run on the full list. 
    # 
    # @param path: [[x, y, z], [x, y, z], ...]
    #
    # @returns pruned_path: [[x, y, z], [x, y, z], ...]
    def prune_and_convert_to_waypoints(self, path):
        if self.constrain:
            init_heading = path[0].heading
            filtered_path = filter(lambda x: x.pinned, path)
            filtered_waypoints = self.to_waypoints(filtered_path)
            start_wp, goal_wp = self.to_waypoints([path[0], path[-1]])

            for waypoint_set in powerset(filtered_waypoints):
                waypoint_list = list(waypoint_set)
                waypoint_path_to_sim = [start_wp] + waypoint_list + [goal_wp]
                collision, final_node = self.simulate_path_through_waypoints(waypoint_path_to_sim, init_heading)
                if not collision:
                    return waypoint_list
        else:
            final_wp = path[-1]
            reverse_pruned_path = [final_wp]
            while final_wp != path[0]:
                i = 0
                while self.path_causes_collision(final_wp, path[i]):
                    i += 1
                reverse_pruned_path.append(path[i])
                final_wp = path[i]

            pruned_path = reverse_pruned_path[::-1] 
            return self.to_waypoints(pruned_path[1:-1])
        raise Exception("precondition violated: path to be pruned does not have subset of nodes that creates collision free path")

    # creates a list from the branch with the leaf node [nn] 
    # 
    # @param    nn: RRTNode
    # @param    start_pos: the root node of the tree
    #
    # @returns  path: [RRTNode(x, y, z), RRTNode(x, y, z), ..., RRTNode(x, y, z)]
    def get_path_from_tree(self, nn, start_pos):
        current_node = nn
        path = [current_node]
        
        while np.linalg.norm(current_node.position - start_pos) > mp_geo.EPSILON:
            current_node = current_node.parent
            path.append(current_node)
        return path[::-1]

    def path_causes_collision(self, new_node, neighbor):
        #TODO: implement prob model to take line, for now we just check collisions with end points
        x,y,z = tuple(new_node.position)
        is_collision = self.prob_model.get_prob(x, y, z, new_node.time_stamp) > self.prob_threshold

        node_diff = new_node.position - neighbor.position
        unit_node_diff = mp_geo.unit_vector(node_diff)

        time_stamp_diff = new_node.time_stamp - neighbor.time_stamp
        i = 1
        while not is_collision and np.linalg.norm(node_diff) > self.collision_increment * i:
            x,y,z = tuple(neighbor.position + unit_node_diff * self.collision_increment * i)
            # approximation of the timestamp that the plane would be at point (x, y, z)
            # initial time stamp plus the ratio of the distance difference times the difference in time stamps
            time_approx = neighbor.time_stamp + (time_stamp_diff * (self.collision_increment * i/np.linalg.norm(node_diff)))
            is_collision = is_collision or self.prob_model.get_prob(x, y, z, time_approx) > self.prob_threshold
            i += 1
        return is_collision 
        
    # Returns the [n] nearest neighbors to [point] of the [tree]
    # 
    # @param    point: np.array([x, y, z])
    # @param    tree: [RRTNode, RRTNode, ..., RRTNode]
    #
    # @returns  path: [RRTNode(x, y, z), RRTNode(x, y, z), ..., RRTNode(x, y, z)]
    def nearest_neighbor(self, point, tree, n):
        np_tree = [x.position for x in tree]
        kd_tree = spatial.cKDTree(np.array(np_tree))
        # query returns distance and index of nn. So, i'm getting the actual node
        dists, nodes = kd_tree.query(point, k=n)
        nodes = nodes[:len(tree)] if n > len(tree) else nodes
        if n == 1:
            return tree[nodes]
        return [tree[n] for n in nodes]       
        
    def simulate_path_through_waypoints(self, waypoints, init_heading):
        collision = False
        path = []
        heading = init_heading
        prev_node = RRTNode(waypoints[0].dv, heading, time_stamp=0)
        for waypoint in waypoints[1:]:
            try:
                new_nodes, _ = self.constrain_movement_towards_point(waypoint.dv, [], prev_node)
            except RRTree.ConstraintViolationException:
                # self.write_tree(path, 'collision_path.debug', waypoints[-1])
                collision = True
                return collision, None
            
            if len(new_nodes) == 0:
                # parent of the current waypoint node
                curr_parent = prev_node
            else:
                curr_parent = new_nodes[-1]
            current_wp_node = RRTNode(waypoint.dv, curr_parent.heading)
            current_wp_node.set_parent(curr_parent)
            curr_parent.add_child(current_wp_node)
            current_wp_node.set_time_stamp(speed=self.get_speed(), prev_time_stamp=curr_parent.time_stamp)
            collision = collision or self.path_causes_collision(curr_parent, current_wp_node)
            '''if collision:
                self.write_tree(path, 'collision_path.debug', waypoints[-1])'''
            heading = curr_parent.heading
            prev_node = RRTNode(current_wp_node.position, heading, time_stamp=0)
            path += new_nodes

        #self.write_tree(path, 'sim_path.debug', waypoints[-1])
        return collision, prev_node
        

    def write_tree(self, tree, file_name, goal_node, timeout=False):
        i = 0
        f = open(str(i) + '_' + file_name, 'a')
        f.write('------\n')
        f.write(str(time.time()) + '\n')
        f.write("obstacles:\n")
        f.write( self.prob_model.print_obst() + '\n')

        f.write('timeout=' + str(timeout) + '\n')
        f.write(str(goal_node[0]) + ' , ' + str(goal_node[1]) + '\n')
        f.write(str(mp_geo.convert_instance.m2ll(goal_node[0], goal_node[1])) + '\n')
        f.write('nodes in tree\n')
        pinned = []
        for node in tree:
            if node.pinned:
                pinned.append(node)
            node_str = ' ' + str(node.position[0]) + ' , ' + str(node.position[1])
            for child in node.children:
                node_str += ' ; ' + str(child.position[0]) + ' , ' + str(child.position[1])
            f.write(node_str + '\n')
        f.write('pinned nodes\n')
        for node in pinned:
            node_str = ' ' + str(node.position[0]) + ' , ' + str(node.position[1]) + ', 10'
            f.write(node_str + '\n')
        f.close()
    
    def write_path(self, lst, file_name, goal_node):
        #print(os.getcwd())
        i = 0
        #while os.path.isfile(str(i) + '_' + file_name) :
        #    i += 1
        f = open(str(i) + '_' + file_name, 'a')
        k = 60
        f.write(str(goal_node) + '\n')
        if lst:
            for node1, node2 in zip(lst, lst[1:]): 
                node_str = str(node1.position[0]) + ',' + str(node1.position[1])
                node_str += ';' + str(node2.position[0]) + ',' + str(node2.position[1])
                node_str += ';' + str(node1.position[0] + k * node1.heading[0]) + ',' + str(node1.position[1] + k * node1.heading[1])
                f.write(node_str + '\n')
            last_node = lst[-1]
            last_node_str = str(last_node.position[0]) + ',' + str(last_node.position[1])
            f.write(last_node_str + '\n')
        f.close()

    def log_waypoints(self, waypoints, file_name, collision):
        f = open(file_name, 'a')
        f.write('------\n')
        f.write('did collide: ' + str(collision) + '\n')
        for wp in waypoints:
            f.write(str(wp.dv[0]) + ', ' + str(wp.dv[1]) + '\n')
        f.close()

        
