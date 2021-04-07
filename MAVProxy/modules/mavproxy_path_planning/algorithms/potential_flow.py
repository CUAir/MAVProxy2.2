import os
import sys
import json
import numpy as np
import shapely.geometry as sg
# import matplotlib.pyplot as plt
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import geometry
import time
from path_planner import PathPlanner

class PotentialFlow(PathPlanner):
    """
    TODO: Add description
    Potential Flow based path planner
    find the most optimum path. Not necessary to avoid all obstacles.
    """

    def __init__(self, factor=150, max_angle=90, radius_for_check=50, spline_params=None, prune=True, buf=50, **kwargs):
        """
        Initializer

        Parameters
        ----------
            factor: float
                TODO
            radius_for_check: int
                TODO
            **kwargs: 
                has information about the obstacles and geofence
        """
        super(PotentialFlow,self).__init__(**kwargs)

        if self.obstacles.size > 0:
            self.centers = self.obstacles[:,:2]
            self.radii = self.obstacles[:,2] + buf
        
        self.max_angle = max_angle
        self.rfc = radius_for_check
        self.factor = np.power(10, factor, dtype=np.float128)
        self.prune = prune

    def plan(self, start, end, prev_wp=None):
        self.start = start
        self.end = end
        self.prev_wp = prev_wp
        old_curr = end
        curr = start
        wps = []
        count = 100
        while np.linalg.norm(end - curr) > self.rfc and (curr != old_curr).all() and count > 0: 
            cost = float("inf")
            best_point = np.array([float('inf'), float('inf')])
            flag = False

            if (old_curr != end).all():
                theta = (np.arctan2((old_curr[1] - curr[1]), (old_curr[0] - curr[0])) * 180 / np.pi)
                angles = list(range(int(theta-self.max_angle) + 180, int(theta+self.max_angle) + 180, 1))

            else:
                if not prev_wp is None:
                    theta = (np.arctan2((prev_wp[1] - start[1]), (prev_wp[0] - start[0])) * 180 / np.pi)
                    angles = list(range(int(theta-self.max_angle/2) + 180, int(theta+self.max_angle/2) + 180, 1))
                else:
                    angles = list(range(0,360,1))

            for angle in angles:
                x,y = self.rfc*np.cos(np.radians(angle))+curr[0], self.rfc*np.sin(np.radians(angle))+curr[1]
                if (curr != old_curr).all():
                    pointcost = self.cost_func(np.asarray([x,y]), start, end)
                    if cost > pointcost:
                        cost = pointcost
                        best_point = np.asarray([x, y])
                        flag = True
            count -= 1
            if flag:
                wps.append(best_point)
                old_curr = curr
                curr = best_point

        if count <= 0:
            print("It took too long ignoring the obstacles.")
            self.path = np.asarray([])
            return self.path

        if len(wps) != 0:
            self.path = np.vstack([start,np.vstack([wps,end])])
        else:
            self.path = np.asarray([])
            return self.path
        if self.prune:
            self.path = self._prune()
        return self.path[2:-1]

    def _prune(self, path=None):
        if path is None:
            path = self.path

        if len(path) > 2:
            pruned_path = [path[-1]]
            l = len(pruned_path)
            i, j = 0, len(path) - 1
            while j > 1:
                while i < j:
                    if not self.is_collision([path[i], path[j]]):
                        j = i
                        i = 0
                        pruned_path.append(path[j])
                    else:
                        i += 1
                if len(pruned_path) == l:
                    pruned_path.append(path[j])
                    j -= 1
                    i = 1
                    l = len(pruned_path)
            pruned_path.append(path[0])
            self.path = np.asarray(pruned_path)
            return self.path[::-1]
        else:
            return path


    def is_collision(self, line):
        collides = False
        for i in range(len(self.obstacles)):
            collides = geometry.point_to_line_dist(self.centers[i], line) < self.radii[i]
            if collides:
                return True
        return False

    def sqr_dists_to_obsts(self, xy):
        if self.obstacles.size < 1:
            # 0 cost for obstacles if there are no obstacles
            return 0 

        d = np.linalg.norm(xy - self.centers, axis=1) - self.radii
        inside = True
        # print("Distance: {}".format(d))
        if self.geofence:
            inside = self.geofence.contains(sg.Point(xy))
        if np.amin(d) < 0 or not inside:
            d = 1e200
        else:
            d = self.factor*np.exp(-d**2, dtype=np.float128)
        return np.sum(d)

    def cost_func(self, xy, start, end):
        pointcost = self.sqr_dists_to_obsts(xy)
        pointcost += -20000/np.linalg.norm(xy - end)**2
        return pointcost

    def plot(self, show=True):
        fig, ax = super(PotentialFlow, self).plot(show=False)
        if not self.prev_wp is None:
            mag = 10
            dx = self.start[0]-self.prev_wp[0]
            dy = self.start[1]-self.prev_wp[1]

            if np.linalg.norm(dx) > 0:
                dx = dx/np.linalg.norm(dx)
            if np.linalg.norm(dy) > 0:
                dy = dy/np.linalg.norm(dy)
            ax.arrow(self.start[0], self.start[1], mag*dx, mag*dy)
        if show:
            plt.show()
        return fig, ax

if __name__ == "__main__":
    
    geofence = sg.Polygon([(-100, -100), (-100, 200), (200, 200), (200, -100)])
    start = np.asarray([70.0,20.0])
    end = np.asarray([50.0,150.0])

    prev_wp = np.asarray([70.0,30])

    obstacles = np.array([[100,40,20],
                          [40,100,30]])

    planner = PotentialFlow(geofence=geofence, obstacles=obstacles)
    waypoints = planner.plan(start,end, prev_wp=prev_wp)

    print(planner.metric())
    planner.plot()

