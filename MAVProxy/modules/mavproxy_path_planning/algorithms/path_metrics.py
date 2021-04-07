#spline enters geofence 
#spline enters obstacles
#number of obstacles hit

#return an object: 
#		Stats for obstacles hit (which ones)
#		Score for total path created 
# 		distance 
#		Number of waypoints placed 
#		Feasibility: max angle
#       closest distance to obstacle 
# 		area covered by path (coverage)

#Add this as a function in the path_planner class 

import sys
sys.path.append("..")
from path_planner import PathPlanner 
from splines import Splines 
import numpy as np

class PathMetrics():
	def __init__(PathPlanner):
