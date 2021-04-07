import numpy as np
# import matplotlib.pyplot as plt
from shapely.geometry import LineString

import geometry 
from splines import Splines

class PathPlanner(object):
    """
    Abstract class which requires a method to plan a path between a pair of waypoints.
    All classes which contain path planning algorithms should subclass this class.

    Attributes
    ----------------------
        geofence: shapely.geometry.Polygon
            Geofencing for the perimeter of search.

        obstacles: ndarray
            2D array with each element representing an obstacle as [x,y,radius]

        path: ndarray
            2D array with each element representing a waypoint as [x,y]. 
            Does not include `start` and `end` points.

    """

    def __init__(self, geofence=None, obstacles=None):
        """
        Initialize the clas attributes.

        Parameters
        ----------------------
            geofence: shapely.geometry.Polygon
                Geofencing for the perimeter of search.

            obstacles: ndarray
                2D array with each element representing an obstacle as [x,y,radius]
        """

        self.geofence = geofence
        self.obstacles = obstacles
        self.path = None

    def plan(self, start, end):
        """
        Finds a path from the start to the goal hopefully avoiding obstacles.
        
        Parameters
        ----------------------
            start: ndarray
                1D array with [x,y] of the initial point.
            end: ndarray
                1D array with [x,y] of the end point.

        Returns
        ----------------------
            path: ndarray
                2D array with each element representing a waypoint as [x,y]. 
                Does not include `start` and `end` points.
        """
        raise NotImplementedError

    def metric(self, path=None, t=3):
        """
        Calculates how good the path is by giving information about it in an object format:
        TODO: Use Spline functions to do the metrics
        Parameters
        ----------------------
            path : ndarray 
                Array of waypoints containing the start and the end, if it is none self.path is used instead.

            t : int 
                Thickness of the path for coverage

        Returns
        ----------------------
            metric : dict
                     A dictionary with the values of different parameters to analyze the path planned.
                     {
                        "distance": distance of the entire path
                        "num_waypoints": the number of extra waypoints (other than the start and goal) the path contains
                        "max_angle": maximum angle turn the path makes
                        "num_collision": counts the number of obstacles hit
                        "coverage": the area covered by the path
                        "obs_dist": is the sum of the distances from each obstacle for each segment of path
                        "closest_obs_dist" : distance to the closest obstacle
                        "is_spline": boolean for if it is a spline or not
                     } 
        """
        if path is None:
            path = self.path

        if not path is None:
            metric = {}
            metric["distance"] = 0
            metric["max_angle"] = 0
            metric["closest_obs_dist"] = float("inf")
            metric["num_collisions"] = 0
            metric["is_spline"] = type(path) == Splines

            if metric["is_spline"]:
                metric["num_waypoints"] = len(path.beziers) - 1
                points = np.asarray([])
                for curve in path.beziers:
                    metric["distance"] += curve.length
                    if len(points) == 0:
                        points = curve.evaluate_multi(np.linspace(0.0,1.0,num=20)).T
                    else: 
                        points = np.vstack((points,curve.evaluate_multi(np.linspace(0.0,1.0,num=20)).T))

                line_string = LineString(points)
                metric["coverage"] = line_string.buffer(t).area

                e = (points[1]-points[0])/np.linalg.norm(points[1]-points[0])
                for i in range(len(points)-1):
                    v = points[i+1]-points[i]
                    metric["obs_dist"] = 0
                    for obs in self.obstacles:
                        obs_dist = geometry.point_to_line_dist(obs[:2], [points[i], points[i+1]])
                        if obs_dist <= obs[2]:
                            metric["num_collisions"] += 1
                        metric["obs_dist"] += obs_dist
                        if metric["closest_obs_dist"] > obs_dist:
                            metric["closest_obs_dist"] = obs_dist

                    if i > 0:
                        angle = np.arccos(v.dot(e)/np.linalg.norm(v))
                        e = v/np.linalg.norm(v)
                        if angle > metric["max_angle"]:
                            metric["max_angle"] = angle 
                return metric 

            else:
                metric["num_waypoints"] = len(path) - 2
                line_string = LineString(path)
                metric["coverage"] = line_string.buffer(t).area

                e = (path[1]-path[0])/np.linalg.norm(path[1]-path[0])

                for i in range(len(path)-1):
                    v = path[i+1]-path[i]
                    metric["obs_dist"] = 0
                    for obs in self.obstacles:
                        obs_dist = geometry.point_to_line_dist(obs[:2], [path[i], path[i+1]])
                        if obs_dist <= obs[2]:
                            metric["num_collisions"] += 1
                        metric["obs_dist"] += obs_dist
                        if metric["closest_obs_dist"] > obs_dist:
                            metric["closest_obs_dist"] = obs_dist

                    metric["distance"] += np.linalg.norm(v)
                    if i > 0:
                        angle = np.arccos(v.dot(e)/np.linalg.norm(v))
                        e = v/np.linalg.norm(v)
                        if angle > metric["max_angle"]:
                            metric["max_angle"] = angle

                return metric
        else:
            raise ValueError('No path was found. Did you plan before calling this?')

    def plot(self, path=None, show=True):
        """
        Method to plot a path and obstacles.

        Parameters
        ----------------------------
            path : ndarray
                Array with waypoints. including the start and end.

            show : boolean
                Flag to run plt.show() or not, default is True.

        Returns
        ----------------------------
            fig, ax : 
                Matplotlib figure and axis to plot later
        """

        if path is None:
            path = self.path

        fig, ax = plt.subplots()
        plt.gca().set_aspect('equal', adjustable='box')

        for obs in self.obstacles:
                circle = plt.Circle((obs[0], obs[1]), obs[2], color='b', alpha=0.3)
                ax.add_artist(circle)

        if type(path) == Splines:
            # Plotting the splines
            path.plot(fig=fig, ax=ax)

            # Star and End are green dots
            ax.plot(path.waypoints[0,0], path.waypoints[0,1],"go")
            ax.plot(path.waypoints[-1,0], path.waypoints[-1,1],"go")
        else:
            # Path are red lines with red waypoint dots
            ax.plot(path[:,0], path[:,1],"r-")
            ax.plot(path[:,0], path[:,1],"ro")

            # Star and End are green dots
            ax.plot(path[0,0], path[0,1],"go")
            ax.plot(path[-1,0], path[-1,1],"go")

        if not self.geofence is None:
            xs, ys = self.geofence.exterior.xy
            ax.fill(xs, ys, alpha=0.5, fc='r', ec='none')

        if show:
            plt.show()

        return fig, ax


