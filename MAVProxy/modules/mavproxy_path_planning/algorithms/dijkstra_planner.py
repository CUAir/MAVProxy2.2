import sys
import heapq
import numpy as np 
import matplotlib.pyplot as plt

from path_planner import PathPlanner

class DijkstraPlanner(PathPlanner):
    def __init__(self, converter, obstacles=None, num_sides=6, pad=50, geofence=None):
        obstacles = np.vstack([obstacles[0],obstacles[1]]).T
        super(DijkstraPlanner, self).__init__(converter, geofence, obstacles)
        self.graph = {}
        self.num_sides = num_sides
        self.pad = pad
        
    def plan(self, start, end):
        vertices = self._get_vertices(start, end, self.num_sides, self.pad)
        self._make_graph(vertices)
        g = Graph(self.graph)
        nodes = g.shortest_path(0,1)
        path = []
        for i in range(len(nodes)-1):
            path.append(vertices[nodes[i]])
        path = np.asarray(path)
        return path.reshape(2,-1)

    def _make_graph(self, vertices):
        for i in range(len(vertices)):
            edges = {}
            for j in range(len(vertices)):
                # No self looping edges
                if i == j:
                    continue

                # If the edge colides set the edge weight is infinite
                n = self._collision(vertices[i], vertices[j])
                edges[j] = 100000*n
                # Else the distance is the edge weight
                edges[j] += np.linalg.norm(vertices[i] - vertices[j])

            self.graph[i] = edges
        
    def _get_vertices(self, start, end, num_sides, pad):
        # theta = 2*np.pi/num_sides
        # R = np.array([[np.cos(theta), -np.sin(theta), 0],
        #              [np.sin(theta), np.cos(theta), 0],
        #              [0, 0, 1]])

        # vertices = []
        # vertices.append(start)
        # vertices.append(end)
        # for obs in self.obstacles:
        #     r = obs[2]*np.sqrt(1+(np.tan(theta/2))**2)
        #     p = np.array([r + pad, 0, 1])
        #     vertices.append(p.T[:-1]+[obs[0], obs[1]])
        #     for i in range(num_sides-1):
        #         p = R.dot(p.T).T
        #         vertices.append(p.T[:-1]+[obs[0], obs[1]])
        # vertices = np.asarray(vertices)
        # return vertices

        theta = 2*np.pi/num_sides
        R = np.array([[np.cos(theta), -np.sin(theta), 0],
                     [np.sin(theta), np.cos(theta), 0],
                     [0, 0, 1]])

        vertices = []
        vertices.append(np.asarray([self.waypoints[0][0],self.waypoints[0][1]]))
        vertices.append(np.asarray([self.waypoints[1][0],self.waypoints[1][1]]))
        fig, ax = plt.subplots()
        plt.gca().set_aspect('equal', adjustable='box')

        for obs in self.obstacles:
            r = obs[2]*np.sqrt(1+(np.tan(theta/2))**2)
            p = np.array([r + pad, 0, 1])
            vertices.append(p.T[:-1]+[obs[0], obs[1]])
            for i in range(num_sides-1):
                p = R.dot(p.T).T
                vertices.append(p.T[:-1]+[obs[0], obs[1]])

            circle = plt.Circle((obs[0], obs[1]), obs[2], color='b', alpha=0.3)
            ax.add_artist(circle)
            # x_max, x_min, y_max, y_min = obs[0] + obs[2] + pad, obs[0] - obs[2] - pad, \
                                         # obs[1] + obs[2] + pad, obs[1] - obs[2] - pad
            # vertices.append(np.asarray([x_max, y_max]))
            # vertices.append(np.asarray([x_max, y_min]))
            # vertices.append(np.asarray([x_min, y_max]))
            # vertices.append(np.asarray([x_min, y_min]))
        vertices = np.asarray(vertices)
        
        # plt.ylim(-5,5)
        # plt.xlim(-5,5)
        plt.plot(vertices[2:,0], vertices[2:,1],"ro")
        return vertices

    def _collision(self, vertex_1, vertex_2):
        count = 0
        for obs in self.obstacles:
            obs_center = obs[:2] 
            obs_radius = obs[-1]
            line = [vertex_1, vertex_2]
            min_dist = self._point_to_line_dist(obs_center, line)
            if min_dist <= obs_radius:
                count += 1
        return count

    # https://stackoverflow.com/questions/27161533/find-the-shortest-distance-between-a-point-and-line-segments-not-line
    def _point_to_line_dist(self, point, line):
        """Calculate the distance between a point and a line segment.

        To calculate the closest distance to a line segment, we first need to check
        if the point projects onto the line segment.  If it does, then we calculate
        the orthogonal distance from the point to the line.
        If the point does not project to the line segment, we calculate the 
        distance to both endpoints and take the shortest distance.

        :param point: Numpy array of form [x,y], describing the point.
        :type point: numpy.core.multiarray.ndarray
        :param line: list of endpoint arrays of form [P1, P2]
        :type line: list of numpy.core.multiarray.ndarray
        :return: The minimum distance to a point.
        :rtype: float
        """
        # unit vector
        unit_line = line[1] - line[0]
        norm_unit_line = unit_line / np.linalg.norm(unit_line)

        # compute the perpendicular distance to the theoretical infinite line
        segment_dist = (
            np.linalg.norm(np.cross(line[1] - line[0], line[0] - point)) /
            np.linalg.norm(unit_line)
        )

        diff = (
            (norm_unit_line[0] * (point[0] - line[0][0])) + 
            (norm_unit_line[1] * (point[1] - line[0][1]))
        )

        x_seg = (norm_unit_line[0] * diff) + line[0][0]
        y_seg = (norm_unit_line[1] * diff) + line[0][1]

        endpoint_dist = min(
            np.linalg.norm(line[0] - point),
            np.linalg.norm(line[1] - point)
        )

        # decide if the intersection point falls on the line segment
        lp1_x = line[0][0]  # line point 1 x
        lp1_y = line[0][1]  # line point 1 y
        lp2_x = line[1][0]  # line point 2 x
        lp2_y = line[1][1]  # line point 2 y
        is_betw_x = lp1_x <= x_seg <= lp2_x or lp2_x <= x_seg <= lp1_x
        is_betw_y = lp1_y <= y_seg <= lp2_y or lp2_y <= y_seg <= lp1_y
        if is_betw_x and is_betw_y:
            return segment_dist
        else:
            # if not, then return the minimum distance to the segment endpoints
            return endpoint_dist

class HeapEntry:
    def __init__(self, node, priority):
        self.node = node
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority


class Graph:
    def __init__(self, graph):
        self.nodes = graph

    def add_node(self, key, neighbours):
        self.nodes[key] = neighbours

    def traceback_path(self, target, parents):
        path = []
        while target:
            path.append(target)
            target = parents[target]
        return list(reversed(path))

    def shortest_path(self, start, finish):
        OPEN = [HeapEntry(start, 0.0)]
        CLOSED = set()
        parents = {start: None}
        distance = {start: 0.0}

        while OPEN:
            current = heapq.heappop(OPEN).node

            if current is finish:
                return self.traceback_path(finish, parents)

            if current in CLOSED:
                continue

            CLOSED.add(current)

            for child in self.nodes[current].keys():
                if child in CLOSED:
                    continue
                tentative_cost = distance[current] + self.nodes[current][child]

                if child not in distance.keys() or distance[child] > tentative_cost:
                    distance[child] = tentative_cost
                    parents[child] = current
                    heap_entry = HeapEntry(child, tentative_cost)
                    heapq.heappush(OPEN, heap_entry)
        
    def __str__(self):
        return str(self.vertices)
