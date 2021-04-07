import numpy as np
import bezier.curve as bc
import shapely.geometry as sg
# import matplotlib.pyplot as plt

class Splines(object):
    # waypoints is a list with 2 elements, the numpy arrays of x and y co-ordinates of the waypoints
    # navsp_cp2_sec, navsp_cp3_sec are derived from the parameters from Project Atlas of the same name
    # they, and velocity, are unessicary if linterp is set to True
    # linterp is True if splines should be linearly interpolated, False if splines should be used
    # velocity 
    def __init__(self, wps, velocity=None, navsp_cp2_sec=None, navsp_cp3_sec=None, linterp=False):
        self.linterp = linterp
        self.waypoints = wps
        self.beziers = []
        speed = np.linalg.norm(velocity)
        heading = velocity/speed
        if linterp:
            for i in range(len(wps) - 1):
                pt1, pt2 = wps[i], wps[i+1]
                self.beziers.append(bc.Curve(np.array([pt1,pt2]),1))
        else:
            for i in range(len(wps) - 2):
                pt1, pt2, pt3 = np.array(wps[i]), np.array(wps[i+1]), np.array(wps[i+2])
                cp1 = pt1
                cp4 = pt2
                goal_traj = pt3 - pt2
                scaling_factor = 150 / (np.linalg.norm(goal_traj) ** 2)
                offset = -goal_traj * speed * float(navsp_cp3_sec) * scaling_factor
                cp2 = speed*heading*navsp_cp2_sec + pt1
                cp3 = pt2 + offset
                curve = bc.Curve(np.array([cp1,cp2,cp3,cp4]).T,3)
                self.beziers.append(curve)
                # assume the plane will get to the correct heading
                heading = (pt3 - pt2)/np.linalg.norm(pt3 - pt2)
            self.beziers.append(bc.Curve(np.array([wps[-2],wps[-1]]).T,1))

    # get "points" number of samples from each of the bezier curve
    # at equally spaced times
    def get_samples(self, points=10):
        xs = np.array([])
        ys = np.array([])
        for curve in self.beziers:
            samples = curve.evaluate_multi(np.linspace(0.0,1.0,num=points))
            sample_x,sample_y = samples.T[:,0], samples.T[:,1]
            xs = np.append(xs,sample_x)
            ys = np.append(ys,sample_y)
        return np.array([xs,ys])

    # get the waypoint path in a graphable form
    # if linterp is True it is sufficient to simply return the waypoints
    # otherwise return "points" number of points evenly spaces from each bezier curve
    def get_graphable(self,points=10):
        if self.linterp:
            return np.array(self.waypoints)
        else:
            return self.get_samples(points)

    # returns the waypoints from which the splines were generated
    def get_waypoints(self):
        return self.waypoints

    # returns the sum of lengths of the bezier curves
    def get_length(self):
        l = 0
        for curve in self.beziers:
            l += curve.length
        return l

    # given a cost function of vector inputs, approximates the integral of a cost function over the splines
    # It does this by averaging the function over "points" number of points on each of the splines
    def get_cost(self,cost_function, points=10):
        l = self.get_length()
        samples = self.get_samples(points)
        points = np.swapaxes(samples,0,1)
        dl = l/len(points)
        f = lambda xy: cost_function(xy) * dl
        return np.sum(list(map(f,points)))

    # given a cost function of vector inputs, returns the approximate maximum of the function over the curve
    # by taking the max of the function over "points" number of points from each spline
    def get_cost_max(self, cost_function, points=10):
        samples = self.get_samples(points)
        points = np.swapaxes(samples,0,1)
        return max(list(map(cost_function,points)))

    # returns true if and only if the splines leave the region bounded by the geofence
    # determined by checking whether any of "points" number of points per spline enters the geofence
    def enters_geofence(self, geofence, points=10):
        samples = self.get_samples(points)
        points = np.swapaxes(samples,0,1)
        for pt in points:
            if not sg.Point(pt[0],pt[1]).within(geofence):
                return True
        return False

    # returns the smallest distance from the exterior of any of the obstacles to the point xy
    # returns a negative distance for points inside of the obstacle
    # the obstacles are given as centers, radii
    def get_smallest_dist_to_obst(self, centers, radii, xy):
        squares = np.swapaxes((xy - centers)**2,0,1)
        dists = np.sqrt(squares[0] + squares[1]) - radii
        return np.amin(dists)
    
    # returns true if and only if the splines enter an obstacle
    # determined by checking whether any of "points" number of points per spline enters the obstacle
    def enters_obstacles(self, obstacles, points=10):
        centers = np.swapaxes(obstacles[0],0,1)
        radii = obstacles[1]
        # making the cost negative ensures that a post cost can only occur if 
        # a point lies in the obstacle
        cost = lambda xy : -self.get_smallest_dist_to_obst(centers, radii, xy) 
        return (self.get_cost_max(cost, points) > 0)
        

    # NOT IMPLEMENTED
    # given a vector valued function of vector inputs, approximates the line-integral in the vector field of the cost function
    # It samples points to approximate the integral of the dot product of curve along the vector valued cost function
    def get_vector_cost(self, cost_function, points=10):
        raise NotImplementedError

    def plot(self, fig=None, ax=None, num=50):
        if fig is None or ax is None:
            fig, ax = plt.subplots()
        for curve in self.beziers:
            curve.plot(num, ax=ax)
        return fig, ax

if __name__ == "__main__":
    velocity = 1
    navsp_cp2_sec = 1
    navsp_cp3_sec = 1
    waypoints = np.asarray([[0.0,0.0],
                            [20.0,30.0], 
                            [30.0,30.0]])
    splines = Splines(waypoints, velocity, navsp_cp2_sec, navsp_cp3_sec)
    splines.plot()



