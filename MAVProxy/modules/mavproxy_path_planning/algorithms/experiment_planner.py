import os
import sys
import torch
import numpy as np

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from path_planner import PathPlanner

class ExperimentPlanner(PathPlanner):
    """
    TODO: Add description
    Potential Flow based path planner
    find the most optimum path. Not necessary to avoid all obstacles.
    """

    def __init__(self, initializer=0, spline_params=None, **kwargs):
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
        super(ExperimentPlanner,self).__init__(**kwargs)

    def plan(self, start, end):
        wps = []
        self.path = np.vstack([start,  end])
        return []

    def plot(self, extra=True):
        fig, ax = super(GradientBased,self).plot(show=False)
        print(ax)

if __name__ == "__main__":
    start = np.array([0,0])
    end = np.array([100,100])
    obstacles = np.array([[40,40,30]])
    planner = GradientBased("integral", num_waypoints=1, obstacles=obstacles)
    waypoints = planner.plan(start, end)
    print(planner.metric())
    planner.plot()
