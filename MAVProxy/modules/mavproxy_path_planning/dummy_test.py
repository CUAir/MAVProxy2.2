import numpy as np
from plot import Plot
from splines import Splines
import shapely.geometry as sg
#from modules.mavproxy_path_planning.algorithms.gradient_based import GradientBased
from algorithms.gradient_based import GradientBased
from algorithms.potential_flow import PotentialFlow

case = 4
if case == 1:
    geofence = sg.Polygon([(-200, 0), (0, 400), (200, 0), (50,-50), (0, -400)])
    x = np.array([10.0,20.0,30.0,40.0])
    y = np.array([10.0,30.0,90.0,160.0])
    obstacles = (np.array([[5,10,40],[30,40,20]]),np.array([10,20,15]))
    splines = Splines([x,y],velocity=np.array([10,0]),navsp_cp2_sec=1,navsp_cp3_sec=1,linterp=False)
    f = lambda xy : xy[0] + xy[1]
    f = lambda xy : 1
    print(splines.get_cost(f))
    print(splines.get_cost_max(f))
    print(splines.get_length())
    print(splines.enters_geofence(geofence))
    print(splines.enters_obstacles(obstacles))
    my_plot = Plot(geofence,splines,obstacles)
    my_plot.show()
if case == 2:
    geofence = sg.Polygon([(-100, -100), (-100, 200), (200, 200), (200, -100)])
    start = np.array([10.0,10.0])
    end = np.array([70.0,160.0])
    obstacles = (np.array([[1000],[1000]]),np.array([10]))
    obstacles = (np.array([[70,100,40],[30,40,100]]),np.array([10,20,30]))
    planner = GradientBased('integral',None,obstacles)
    waypoints = planner.plan(start,end)
    start = start.reshape(2,-1)
    end = end.reshape(2,-1)
    waypoints = np.append(start,np.append(waypoints,end,axis=1),axis=1)
    splines = Splines(waypoints,velocity=np.array([5,0]),navsp_cp2_sec=1,navsp_cp3_sec=1,linterp=False)
    print(splines.enters_geofence(geofence))
    print(splines.enters_obstacles(obstacles))
    function = lambda x,y: np.array([[planner.point_cost(np.array([x[i][j],y[i][j]])) for j in range(len(x[0]))] for i in range(len(x))])
    my_plot = Plot(geofence,splines,obstacles, function)
    my_plot.show()
if case == 3:
    geofence = sg.Polygon([(-100, -100), (-100, 200), (200, 200), (200, -100)])
    start = np.array([100.0,10.0])
    end = np.array([50.0,150.0])
    obstacles = (np.array([[70,100,40],[30,40,100]]),np.array([10,20,30]))
    planner = PotentialFlow(None, obstacles)
    waypoints = planner.plan(start,end)
    start_prime = start.reshape(2,-1)
    end_prime = end.reshape(2,-1)
    waypoints = np.append(start_prime,np.append(waypoints,end_prime,axis=1),axis=1)
    splines = Splines(waypoints,velocity=np.array([5,0]),navsp_cp2_sec=1,navsp_cp3_sec=1,linterp=True)
    print(splines.enters_geofence(geofence))
    print(splines.enters_obstacles(obstacles))
    function = lambda x,y: np.squeeze(np.array([[planner.cost_func(np.array([x[i][j],y[i][j]]), start, end) for j in range(len(x[0]))] for i in range(len(x))]))
    my_plot = Plot(geofence,splines,obstacles,function)
    my_plot.show()
if case == 4:
    geofence = sg.Polygon([(-100, -100), (-100, 200), (200, 200), (200, -100)])
    start = np.array([100.0,10.0])
    end = np.array([50.0,150.0])
    obstacles = (np.array([[70,100,40, 103],[30,40,100, 105]]),np.array([10,20,30, 20]))
    planner = PotentialFlow(None, obstacles)
    waypoints = planner.plan(start,end)
    planner = GradientBased('integral', None, obstacles, waypoints)
    waypoints = planner.plan(start, end)
    start_prime = start.reshape(2,-1)
    end_prime = end.reshape(2,-1)
    waypoints = np.append(start_prime,np.append(waypoints,end_prime,axis=1),axis=1)
    splines = Splines(waypoints,velocity=np.array([5,0]),navsp_cp2_sec=1,navsp_cp3_sec=1,linterp=False)
    print(splines.enters_geofence(geofence))
    print(splines.enters_obstacles(obstacles))
    function = lambda x,y: np.array([[planner.point_cost(np.array([x[i][j],y[i][j]])) for j in range(len(x[0]))] for i in range(len(x))])
    my_plot = Plot(geofence,splines,obstacles, function)
    my_plot.show()
else:
    raise NotImplementedError
