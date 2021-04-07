import os
import sys
import numpy as np
import shapely.geometry as sg
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import geometry
from path_planner import PathPlanner

class LucaPlanner(PathPlanner):
    def __init__(self,**kwargs):
        """
        Initializer

        Parameters
        ----------
            
        """
        super(LucaPlanner,self).__init__(**kwargs)


        self.obs_shape = []
        if not self.obstacles is None:
            self.centers = self.obstacles[:,:2]
            self.radii = self.obstacles[:,2]
        for i in range(len(self.centers)):
            self.obs_shape.append(sg.Point(self.centers[i]).buffer(self.radii[i]))

    def plan(self, start, end):
        wps = []
        self.path = np.vstack([start,  end])
        count_collision = 10000
        prev = start
        wps = []
        while True:
            collision = self.get_collision(np.vstack([prev,  end]))
            if not collision is None:
                points, center, r = collision
            else:
                break
            mid = (points[0] + points[1])/2 
            A = np.linalg.norm(prev - center)
            B = np.linalg.norm(mid - prev)
            C = np.linalg.norm(mid - center)
            theta = np.arcsin(r/A)
            alpha = np.arctan2(C,B)
            # print(theta>alpha)
            closer = points[0] if np.linalg.norm(points[0] - prev) > np.linalg.norm(points[1] - prev) else points[1]
            if (center[1]-prev[1])/(center[0]-prev[0]) > (closer[1]-prev[1])/(closer[0]-prev[0]):
                D = -B*np.tan(theta - alpha)
            else:
                D = B*np.tan(theta - alpha)

            rot = np.arctan2(points[1][1]-points[0][1], points[1][0]-points[0][0])
            c, s = np.cos(rot), np.sin(rot)
            R = np.array(((c,-s), (s, c)))
            p = prev + R.dot(np.asarray([[B],[D]])).T
            prev = p
            wps.append(p)
            
            
            # A = np.linalg.norm(prev- mid)
            # z = np.sqrt(A**2 - r**2)
            # y = r**2/z
            # x = np.sqrt(y**2 + r**2)
            # theta = np.arctan2(x, A)
            # d = z + y
            # alpha = np.arctan2(points[1][1]-points[0][1], points[1][0]-points[0][0])
            # p = prev + np.asarray([d*np.cos(alpha+theta), d*np.sin(alpha+theta)])

            # wps =np.vstack([points[0],  p , points[1]])

        wps =np.asarray(wps).reshape(-1,2)
        self.path = np.vstack([start,np.vstack([wps,end])])
        return self.path


    
    def get_collision(self, path):
        for j in range(len(path)-1):
            line = sg.LineString([path[j], path[j+1]])
            for i in range(len(self.obs_shape)): 
                intersect = line.intersection(self.obs_shape[i])
                if not intersect.is_empty:
                    print(intersect)
                    return np.asarray(intersect.coords).reshape(-1,2), self.centers[i], self.radii[i]



    def is_collision(self, line):
        collides = False
        for obs in self.obstacles:
            collides = geometry.point_to_line_dist(obs[:2], line) < obs[2]
            if collides:
                return True
        return False

if __name__ == "__main__":
    
    # geofence = sg.Polygon([(-100, -100), (-100, 200), (200, 200), (200, -100)])
    start = np.asarray([0.0,0.0])

    end = np.asarray([5.0,10.0])

    obstacles = np.array([[1.5,3.5,1]])

    planner = LucaPlanner( obstacles=obstacles)
    waypoints = planner.plan(start,end)
    planner.plot()