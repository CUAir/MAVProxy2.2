import math
import random
import uuid
from operator import itemgetter
import numpy as np 
from rtree import index
import matplotlib.pyplot as plt



def cost_to_go(a: tuple, b: tuple) -> float:
    """
    :param a: current location
    :param b: next location
    :return: estimated segment_cost-to-go from a to b
    """
    return distance_between_points(a, b)


def path_cost(E, a, b):
    """
    Cost of the unique path from x_init to x
    :param E: edges, in form of E[child] = parent
    :param a: initial location
    :param b: goal location
    :return: segment_cost of unique path from x_init to x
    """
    cost = 0
    while not b == a:
        p = E[b]
        cost += distance_between_points(b, p)
        b = p

    return cost


def segment_cost(a, b):
    """
    Cost function of the line between x_near and x_new
    :param a: start of line
    :param b: end of line
    :return: segment_cost function between a and b
    """
    return distance_between_points(a, b)



class RRTStarPlanner():
    def __init__(self, converter, geofence=None, obstacles = None):
        self.converter = converter
        self.geofence = geofence
        self.obstacles = obstacles
        
        self.obstacles = self.obstacles_to_rect()
        self.Q = np.array([(8, 4)])  # length of tree edges
        self.r = 1  # length of smallest edge to check for intersection with obstacles
        self.max_samples = 1024  # max number of samples to take before timing out
        self.prc = 0.1  # probability of checking for a connection to goal
        self.rewire_count = 32
        X_dimensions = np.array([(0, 200), (0, 200)])
        self.X = SearchSpace(X_dimensions, self.obstacles) # search space
        self.rrt = RRTStar(self.X, self.Q, start, end, self.max_samples, self.r,self.rewire_count)


    def obstacles_to_rect(self):
        bbox = []

        for obs in self.obstacles:
            bbox.append([obs[0]-obs[2], obs[1]-obs[2],
                         obs[0]+obs[2], obs[1]+obs[2],])
        return bbox

    def plan(self, start, end):
        
        path = self.rrt.rrt_star()
        return np.asarray(path)

class Tree(object):
    def __init__(self, X):
        """
        Tree representation
        :param X: Search Space
        """
        p = index.Property()
        p.dimension = X.dimensions
        self.V = index.Index(interleaved=True, properties=p)  # vertices in an rtree
        self.V_count = 0
        self.E = {}  # edges in form E[child] = parent

def distance_between_points(a, b):
    """
    Return the Euclidean distance between two points
    :param a: first point
    :param b: second point
    :return: Euclidean distance between a and b
    """
    distance = sum(map(lambda a_b: (a_b[0] - a_b[1]) ** 2, zip(a, b)))

    return math.sqrt(distance)

class RRTStar(object):
    def __init__(self, X, Q, x_init, x_goal, max_samples, r, rewire_count,prc=0.01):
        """
        Template RRT planner
        :param X: Search Space
        :param Q: list of lengths of edges added to tree
        :param x_init: tuple, initial location
        :param x_goal: tuple, goal location
        :param max_samples: max number of samples to take
        :param r: resolution of points to sample along edge when checking for collisions
        :param prc: probability of checking whether there is a solution
        """
        self.X = X
        self.samples_taken = 0
        self.max_samples = max_samples
        self.Q = Q
        self.r = r
        self.prc = prc

        self.x_init = x_init
        self.x_goal = x_goal

        self.trees = []  # list of all trees
        self.add_tree()  # add initial tree
        self.rewire_count = rewire_count if rewire_count is not None else 0
        self.c_best = float('inf')  # length of best solution thus far

    def add_tree(self):
        """
        Create an empty tree and add to trees
        """
        self.trees.append(Tree(self.X))

    def add_vertex(self, tree, v):
        """
        Add vertex to corresponding tree
        :param tree: int, tree to which to add vertex
        :param v: tuple, vertex to add
        """
        self.trees[tree].V.insert(0, v + v, v)
        self.trees[tree].V_count += 1  # increment number of vertices in tree
        self.samples_taken += 1  # increment number of samples taken

    def add_edge(self, tree, child, parent):
        """
        Add edge to corresponding tree
        :param tree: int, tree to which to add vertex
        :param child: tuple, child vertex
        :param parent: tuple, parent vertex
        """
        self.trees[tree].E[child] = parent

    def nearby(self, tree, x, n):
        """
        Return nearby vertices
        :param tree: int, tree being searched
        :param x: tuple, vertex around which searching
        :param n: int, max number of neighbors to return
        :return: list of nearby vertices
        """
        return list(self.trees[tree].V.nearest(x, num_results=n, objects="raw"))

    def get_nearest(self, tree, x):
        """
        Return vertex nearest to x
        :param tree: int, tree being searched
        :param x: tuple, vertex around which searching
        :return: tuple, nearest vertex to x
        """
        return self.nearby(tree, x, 1)[0]

    def new_and_near(self, tree, q):
        """
        Return a new steered vertex and the vertex in tree that is nearest
        :param tree: int, tree being searched
        :param q: length of edge when steering
        :return: vertex, new steered vertex, vertex, nearest vertex in tree to new vertex
        """
        x_rand = self.X.sample_free()
        x_nearest = self.get_nearest(tree, x_rand)
        x_new = self.steer(x_nearest, x_rand, q[0])
        # check if new point is in X_free and not already in V
        if not self.trees[0].V.count(x_new) == 0 or not self.X.obstacle_free(x_new):
            return None, None

        self.samples_taken += 1

        return x_new, x_nearest

    def connect_to_point(self, tree, x_a, x_b):
        """
        Connect vertex x_a in tree to vertex x_b
        :param tree: int, tree to which to add edge
        :param x_a: tuple, vertex
        :param x_b: tuple, vertex
        :return: bool, True if able to add edge, False if prohibited by an obstacle
        """
        if self.trees[tree].V.count(x_b) == 0 and self.X.collision_free(x_a, x_b, self.r):
            self.add_vertex(0, x_b)
            self.add_edge(0, x_b, x_a)

            return True

        return False

    def can_connect_to_goal(self, tree):
        """
        Check if the goal can be connected to the graph
        :param tree: rtree of all Vertices
        :return: True if can be added, False otherwise
        """
        x_nearest = self.get_nearest(tree, self.x_goal)
        if self.x_goal in self.trees[tree].E and x_nearest in self.trees[tree].E[self.x_goal]:
            # tree is already connected to goal using nearest vertex
            return True

        if self.X.collision_free(x_nearest, self.x_goal, self.r):  # check if obstacle-free
            return True

        return False

    def get_path(self):
        """
        Return path through tree from start to goal
        :return: path if possible, None otherwise
        """
        if self.can_connect_to_goal(0):
            print("Can connect to goal")
            self.connect_to_goal(0)

            return self.reconstruct_path(0, self.x_init, self.x_goal)

        print("Could not connect to goal")

        return None

    def connect_to_goal(self, tree):
        """
        Connect x_goal to graph
        (does not check if this should be possible, for that use: can_connect_to_goal)
        :param tree: rtree of all Vertices
        """
        x_nearest = self.get_nearest(tree, self.x_goal)
        self.trees[tree].E[self.x_goal] = x_nearest

    def steer(self, start, goal, distance):
        """
        Return a point in the direction of the goal, that is distance away from start
        :param start: start location
        :param goal: goal location
        :param distance: distance away from start
        :return: point in the direction of the goal, distance away from start
        """
        ab = np.empty(len(start), np.float)  # difference between start and goal
        for i, (start_i, goal_i) in enumerate(zip(start, goal)):
            ab[i] = goal_i - start_i

        ab = tuple(ab)
        zero_vector = tuple(np.zeros(len(ab)))

        ba_length = distance_between_points(zero_vector, ab)  # get length of vector ab
        unit_vector = np.fromiter((i / ba_length for i in ab), np.float, len(ab))
        # scale vector to desired length
        scaled_vector = np.fromiter((i * distance for i in unit_vector), np.float, len(unit_vector))
        steered_point = np.add(start, scaled_vector)  # add scaled vector to starting location for final point

        # if point is out-of-bounds, set to bound
        for dim, dim_range in enumerate(self.X.dimension_lengths):
            if steered_point[dim] < dim_range[0]:
                steered_point[dim] = dim_range[0]
            elif steered_point[dim] > dim_range[1]:
                steered_point[dim] = dim_range[1]

        return tuple(steered_point)

    def reconstruct_path(self, tree, x_init, x_goal):
        """
        Reconstruct path from start to goal
        :param tree: int, tree in which to find path
        :param x_init: tuple, starting vertex
        :param x_goal: tuple, ending vertex
        :return: sequence of vertices from start to goal
        """
        path = [x_goal]
        current = x_goal
        if x_init == x_goal:
            return path
        while not self.trees[tree].E[current] == x_init:
            path.append(self.trees[tree].E[current])
            current = self.trees[tree].E[current]
        path.append(x_init)
        path.reverse()

        return path

    def rrt_search(self):
        """
        Create and return a Rapidly-exploring Random Tree, keeps expanding until can connect to goal
        https://en.wikipedia.org/wiki/Rapidly-exploring_random_tree
        :return: list representation of path, dict representing edges of tree in form E[child] = parent
        """
        self.add_vertex(0, self.x_init)
        self.add_edge(0, self.x_init, None)

        while True:
            for q in self.Q:  # iterate over different edge lengths
                for i in range(q[1]):  # iterate over number of edges of given length to add
                    x_new, x_nearest = self.new_and_near(0, q)
                    if x_new is None:
                        continue

                    # connect shortest valid edge
                    self.connect_to_point(0, x_nearest, x_new)

                    # probabilistically check if solution found
                    if self.prc and random.random() < self.prc:
                        print("Checking if can connect to goal at", str(self.samples_taken), "samples")
                        path = self.get_path()
                        if path is not None:
                            return path

                    # check if can connect to goal after generating max_samples
                    if self.samples_taken >= self.max_samples:
                        return self.get_path()

    def get_nearby_vertices(self, tree, x_init, x_new):
        """
        Get nearby vertices to new vertex and their associated costs, number defined by rewire count
        :param tree: tree in which to search
        :param x_init: starting vertex used to calculate path cost
        :param x_new: vertex around which to find nearby vertices
        :return: list of nearby vertices and their costs, sorted in ascending order by cost
        """
        X_near = self.nearby(tree, x_new, self.current_rewire_count(tree))
        L_near = [(x_near, path_cost(self.trees[tree].E, x_init, x_near) + segment_cost(x_near, x_new)) for
                  x_near in X_near]
        # noinspection PyTypeChecker
        L_near.sort(key=itemgetter(0))

        return L_near

    def rewire(self, tree, x_new, L_near):
        """
        Rewire tree to shorten edges if possible
        Only rewires vertices according to rewire count
        :param tree: int, tree to rewire
        :param x_new: tuple, newly added vertex
        :param L_near: list of nearby vertices used to rewire
        :return:
        """
        for x_near, c_near in L_near:
            curr_cost = path_cost(self.trees[tree].E, self.x_init, x_near)
            tent_cost = path_cost(self.trees[tree].E, self.x_init, x_new) + c_near

            if tent_cost < curr_cost and self.X.collision_free(x_near, x_new, self.r):
                self.trees[tree].E[x_near] = x_new

    def connect_shortest_valid(self, tree, x_new, L_near):
        """
        Connect to nearest vertex that has an unobstructed path
        :param tree: int, tree being added to
        :param x_new: tuple, vertex being added
        :param L_near: list of nearby vertices
        """
        # check nearby vertices for total cost and connect shortest valid edge
        for x_near, c_near in L_near:
            if c_near + cost_to_go(x_near, self.x_goal) < self.c_best and self.connect_to_point(tree, x_near, x_new):
                break

    def current_rewire_count(self, tree):
        """
        Return rewire count
        :param tree: tree being rewired
        :return: rewire count
        """
        # if no rewire count specified, set rewire count to be all vertices
        if self.rewire_count is not None:
            return self.trees[tree].V_count

        # max valid rewire count
        return min(self.trees[tree].V_count, self.rewire_count)

    def rrt_star(self):
        """
        Based on algorithm found in: Incremental Sampling-based Algorithms for Optimal Motion Planning
        http://roboticsproceedings.org/rss06/p34.pdf
        :return: set of Vertices; Edges in form: vertex: [neighbor_1, neighbor_2, ...]
        """

        self.add_vertex(0, self.x_init)
        self.add_edge(0, self.x_init, None)

        while True:
            for q in self.Q:  # iterate over different edge lengths
                for i in range(q[1]):  # iterate over number of edges of given length to add
                    x_new, x_nearest = self.new_and_near(0, q)
                    if x_new is None:
                        continue

                    # get nearby vertices and cost-to-come
                    L_near = self.get_nearby_vertices(0, self.x_init, x_new)

                    # check nearby vertices for total cost and connect shortest valid edge
                    self.connect_shortest_valid(0, x_new, L_near)

                    if x_new in self.trees[0].E:
                        # rewire tree
                        self.rewire(0, x_new, L_near)

                    # probabilistically check if solution found
                    if self.prc and random.random() < self.prc:
                        print("Checking if can connect to goal at", str(self.samples_taken), "samples")
                        path = self.get_path()
                        if path is not None:
                            return path

                    # check if can connect to goal after generating max_samples
                    if self.samples_taken >= self.max_samples:
                        return self.get_path()


class SearchSpace(object):
    def __init__(self, dimension_lengths, O=None):
        """
        Initialize Search Space
        :param dimension_lengths: range of each dimension
        :param O: list of obstacles
        """
        # sanity check
        if len(dimension_lengths) < 2:
            raise Exception("Must have at least 2 dimensions")
        self.dimensions = len(dimension_lengths)  # number of dimensions
        # sanity checks
        if any(len(i) != 2 for i in dimension_lengths):
            raise Exception("Dimensions can only have a start and end")
        if any(i[0] >= i[1] for i in dimension_lengths):
            raise Exception("Dimension start must be less than dimension end")
        self.dimension_lengths = dimension_lengths  # length of each dimension
        p = index.Property()
        p.dimension = self.dimensions
        # r-tree representation of obstacles
        # sanity check
        if any(len(o) / 2 != len(dimension_lengths) for o in O):
            raise Exception("Obstacle has incorrect dimension definition")
        if any(o[i] >= o[int(i + len(o) / 2)] for o in O for i in range(int(len(o) / 2))):
            raise Exception("Obstacle start must be less than obstacle end")
        if O is None:
            self.obs = index.Index(interleaved=True, properties=p)
        else:
            self.obs = index.Index(obstacle_generator(O), interleaved=True, properties=p)

    def obstacle_free(self, x):
        """
        Check if a location resides inside of an obstacle
        :param x: location to check
        :return: True if not inside an obstacle, False otherwise
        """
        return self.obs.count(x) == 0

    def sample_free(self):
        """
        Sample a location within X_free
        :return: random location within X_free
        """
        while True:  # sample until not inside of an obstacle
            x = self.sample()
            if self.obstacle_free(x):
                return x

    def collision_free(self, start, end, r):
        """
        Check if a line segment intersects an obstacle
        :param start: starting point of line
        :param end: ending point of line
        :param r: resolution of points to sample along edge when checking for collisions
        :return: True if line segment does not intersect an obstacle, False otherwise
        """
        dist = distance_between_points(start, end)
        # divide line between points into equidistant points at given resolution
        dim_linspaces = [np.linspace(s_i, e_i, int(math.ceil(dist / r))) for s_i, e_i in zip(start, end)]

        coll_free = all(map(self.obstacle_free, zip(*dim_linspaces)))

        return coll_free

    def sample(self):
        """
        Return a random location within X
        :return: random location within X (not necessarily X_free)
        """
        x = np.empty(len(self.dimension_lengths), np.float)
        for dimension in range(len(self.dimension_lengths)):
            x[dimension] = random.uniform(self.dimension_lengths[dimension][0], self.dimension_lengths[dimension][1])

        return tuple(x)


def obstacle_generator(obstacles):
    """
    Add obstacles to r-tree
    :param obstacles: list of obstacles
    """
    for obstacle in obstacles:
        yield (uuid.uuid4(), obstacle, obstacle)

if __name__ == "__main__":
    # geofence = sg.Polygon([(-100, -100), (-100, 200), (200, 200), (200, -100)])
    start = (10,10)
    end = (70,160)
    obstacles = np.array([[70,110,40],[30,40,10]])
    planner = RRTStarPlanner(None, obstacles=obstacles)
    waypoints = planner.plan(start,end)

    def _draw_obstacle(ax, obs):
        circle = plt.Circle((obs[0], obs[1]), obs[2], color='b', alpha=0.3)
        ax.add_artist(circle)

    def _draw_path(ax, path):
        ax.plot(path[:,0], path[:,1],"r-")
        ax.plot(path[:,0], path[:,1],"ro")

    fig, ax = plt.subplots()
    plt.gca().set_aspect('equal', adjustable='box')
    for obs in obstacles:
            _draw_obstacle(ax, obs)

    
    _draw_path(ax, waypoints)
    ax.plot(start[0], start[1],"go")
    ax.plot(end[0], end[1],"go")
    plt.show()

