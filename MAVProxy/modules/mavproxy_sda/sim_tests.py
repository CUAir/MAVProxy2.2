import numpy as np
from sda_rrt import *
import sda_pdriver
import modules.lib.mp_geometry as mp_geo

wps = []
wps.append(mp_geo.Waypoint(167.799944729 , 87.6070684328, 82))
wps.append(mp_geo.Waypoint(-274.883864808 , 112.913069774, 82))
wps.append(mp_geo.Waypoint( -322.284492157 , 90.4343558301, 82))
wps.append(mp_geo.Waypoint( -474.280697487 , 147.694802084, 82))

pdriver = sda_pdriver.ProbDriver(model=sda_pdriver.ProbModelStatic())

pdriver.add_stat_obst(mp_geo.StationaryObstacle(54, np.array([-326.784746894, 157.383587005, 1803.20001595])))
pdriver.add_stat_obst(mp_geo.StationaryObstacle(15.24, np.array([-167.047216609, 219.507556996, 1803.20001595])))
pdriver.generate_model()
test_tree = RRTree(pdriver.current_model, None, increment=5, constrain=True, min_turning_radius=40, timeout=2)

collision, final_node = test_tree.simulate_path_through_waypoints(wps, np.array([0, -1, 0]))
print collision, final_node
