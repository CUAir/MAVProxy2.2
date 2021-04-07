import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from splines import Splines
from path_planner import PathPlanner

class GradientBased(PathPlanner):
    """
    Gradient based path planner, works on different types of cost functions and then minimizes it to 
    find the most optimum path. Not necessary to avoid all obstacles.

    Attributes 
    ----------------

    TODO: Add Attributes
    """
    def __init__(self, cost_type, spline_params=None, initializer=None, num_waypoints=1, **kwargs):
        """
        Initialize the class attributes

        Parameters
        -----------------
            cost_type: str
                Specify the type of cost function the possible options being ['closest', 'integral', 'length']
            
            spline_params: dict
                Parameters for the spline initializations.
                {
                    "velocity" : Velocity for the spline
                    "cp2" : Control Point 2 as metioned in Project Atlas
                    "cp3" : Control Point 3 as metioned in Project Atlas   
                }

            initializer: ndarray
                Initial distribution for the waypoints

            num_waypoints: int
                Only used if initilizer is not to initialize the number of wps

            **kwargs: 
                Has information about the obstacles and geofence
        """
        super(GradientBased,self).__init__(**kwargs)
        assert cost_type in ['closest', 'integral', 'length']

        if not self.obstacles is None:
            self.centers = self.obstacles[:,:2]
            self.radii = self.obstacles[:,2]

        # Cost function initialization
        self.cost_type = cost_type
        cost_functions = {
            "closest": self.closest_cost,
            "integral": self.integral_cost,
            "length": self.length_cost
        }
        self.cost_function = cost_functions[self.cost_type]
        self.num_waypoints = num_waypoints
        # Starting path for the gradient descent
        self.initializer = initializer
        if self.initializer is None:
            # generate the arrays of x and y values for waypoints from a normal distribution
            # TODO: consider altering this distribution to scale to the size of the area
            self.initializer = np.random.randn(num_waypoints,2)
            

        # Spline initialization
        self.velocity = 20
        self.navsp_cp2_sec = 1
        self.navsp_cp3_sec = 1

        if not spline_params is None:
            self.velocity = spline_params["velocity"]
            self.navsp_cp2_sec = spline_params["cp2"]
            self.navsp_cp3_sec = spline_params["cp3"]

    def plan(self, start, end):
        cost_function = lambda wps: self.cost_function(wps, start, end)
        self.initializer = np.asarray([np.linspace(start[0], end[0], self.num_waypoints+2), 
            np.linspace(start[1], end[1], self.num_waypoints+2)]).T[1:-1]

        starting_wps = self.initializer
        result = minimize(cost_function, starting_wps, method='BFGS', options={'disp': True})
        splines = self.get_splines(result.x.reshape(-1,2), start, end)
        self.path = splines
        # self.path = np.vstack([start,np.vstack([result.x.reshape(-1,2),end])])
        return splines
        
    # returns the squared distance from xy to the center of each of the obstacles
    def sqr_dist_to_obsts(self, xy):
        return np.linalg.norm(xy - self.centers, axis=1)**2

    def obstacle_dist_cost(self, xy):
        dist = np.sqrt(self.sqr_dist_to_obsts(xy))
        cost = np.sum((dist > self.radii) * (1/(dist - self.radii)**2)) + np.sum((dist < self.radii) * np.exp(self.radii - dist))
        return cost

    def get_splines(self, waypoints, start, end):
        waypoints = np.vstack([start,np.vstack([waypoints.reshape(-1,2),end])])
        splines = Splines(waypoints, self.velocity, self.navsp_cp2_sec, self.navsp_cp3_sec)
        return splines

    # TODO: Vectorize the self.point_cost function used for the grid plotter
    def closest_cost(self, waypoints, start, end, alpha=0.9):
        splines = self.get_splines(waypoints, start, end)
        self.point_cost = lambda xy : np.amin(1.0/self.sqr_dist_to_obsts(xy))
        print("Max:", splines.get_cost_max(self.point_cost))
        print("Length:", splines.get_length())
        return alpha*splines.get_cost_max(self.point_cost) + (1 - alpha)*splines.get_length()

    def integral_cost(self, waypoints, start, end, c=10):
        splines = self.get_splines(waypoints, start, end)
        self.point_cost = lambda xy : 400*self.obstacle_dist_cost(xy) + c
        return splines.get_cost(self.point_cost)

    def length_cost(self, waypoints, start, end):
        splines = self.get_splines(waypoints, start, end)
        return splines.get_length()

    def plot(self, cost_display=False):
        # TODO: Get the grid to plot properly
        fig, ax = super(GradientBased,self).plot(show=False)

        if cost_display:
            minx, miny, maxx, maxy = -100, 100, -100, 100
            if not self.geofence is None:
                minx, miny, maxx, maxy = self.geofence.bounds
            x,y = np.meshgrid(np.linspace(minx, maxx, 200), np.linspace(miny, maxy, 200))
            coords = np.indices((200,200)).T.reshape(-1,2) - 100
            z = np.asarray([self.point_cost(coord) for coord in coords]).reshape(200, 200).T
            print(np.abs(z).max())
            z_min, z_max = -np.abs(z).max(), np.abs(z).max()
            # z_min = -100
            # z_max = 100
            c = ax.pcolormesh(x, y, z, cmap='RdBu', vmin=z_min, vmax=z_max)
            fig.colorbar(c, ax=ax)
        plt.show()

if __name__ == "__main__":
    # TODO: The plot is weird and not smooth at all
    obstacles = np.array([[40,40,30]])

    planner = GradientBased("integral", num_waypoints=1, obstacles=obstacles)
    start = np.array([0,0])
    end = np.array([100,100])
    waypoints = planner.plan(start, end)
    # print(waypoints)
    print(planner.metric())
    planner.plot(cost_display=False)