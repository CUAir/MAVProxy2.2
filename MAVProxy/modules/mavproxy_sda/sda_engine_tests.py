import unittest
import sys
import os 
import modules.lib.mp_geometry as mp_geo
import copy

class MavproxySDATests(unittest.TestCase):

	def setUp(self):
		sys.path.insert(0, os.path.abspath('../..'))
		from mavproxy import MPState
		from sda_engine import SDAModule
		self.sda_engine = SDAModule(MPState(sdatester=True))
		wp1 = mp_geo.Waypoint(10, 10, 10, sda=False)
		wp2 = mp_geo.Waypoint(20, 10, 10, sda=False)
		wp3 = mp_geo.Waypoint(30, 10, 10, sda=False)
		wp4 = mp_geo.Waypoint(40, 10, 10, sda=False)
		wp5 = mp_geo.Waypoint(50, 10, 10, sda=False)

		self.sda_engine.wplist = [wp1, wp2, wp3, wp4, wp5]

	def test_get_index_of_ith_perm_waypoint_after_current(self):
		for curr in range(len(self.sda_engine.wplist)): 
		 	for i in range(len(self.sda_engine.wplist) - curr):
		 		index = self.sda_engine.get_index_of_ith_perm_waypoint_after_current(i, curr_wp_index=curr)
		 		correct_answer = -1 if i == 0 else i + curr
		 		self.assertEqual(index, correct_answer)

		# Is SDA? [False, True, True, False, True, False, True, True, False, False] 	
		sda_wp1 = mp_geo.Waypoint(15, 10, 10, sda=True)
		sda_wp2 = mp_geo.Waypoint(25, 10, 10, sda=True)

		self.sda_engine.wplist.insert(1, sda_wp1)
		self.sda_engine.wplist.insert(2, sda_wp2)

		sda_wp3 = mp_geo.Waypoint(35, 10, 10, sda=True)

		self.sda_engine.wplist.insert(4, sda_wp3)

		sda_wp4 = mp_geo.Waypoint(45, 10, 10, sda=True)
		sda_wp5 = mp_geo.Waypoint(55, 10, 10, sda=True)

		self.sda_engine.wplist.insert(6, sda_wp4)
		self.sda_engine.wplist.insert(7, sda_wp5)

		# Is SDA? [False, True, True, False, True, False, True, True, False, False] 
		#[0, 3, 5, 8, 9]
		correct_answers = [ [-1, 3, 5, 8, 9],
							[-1, 3, 5, 8, 9],
							[-1, 3, 5, 8, 9],
							[-1, 5, 8, 9],
							[-1, 5, 8, 9],
							[-1, 8, 9],
							[-1, 8, 9],
							[-1, 8, 9],
							[-1, 9],
							[-1]]

		perm_wp_left = len(correct_answers[0]) 
		for curr in range(len(self.sda_engine.wplist)): 
			if not self.sda_engine.wplist[curr].sda:
				perm_wp_left -= 1
		 	for i in range(len(self.sda_engine.wplist)):
		 		index = self.sda_engine.get_index_of_ith_perm_waypoint_after_current(i, curr_wp_index=curr)
		 		if i > perm_wp_left:
		 			correct_answer = -1
		 		else: 
		 			correct_answer = correct_answers[curr][i]
		 		self.assertEqual(index, correct_answer)	 
	
	def test_update_path_to_wp_at_index(self):

		init_wplist_len = len(self.sda_engine.wplist)
		init_wplist = copy.copy(self.sda_engine.wplist)

		sda_wp1 = mp_geo.Waypoint(15, 10, 10, sda=True)
		sda_wp2 = mp_geo.Waypoint(25, 10, 10, sda=True)
		sda_wp3 = mp_geo.Waypoint(35, 10, 10, sda=True)
		sda_wp4 = mp_geo.Waypoint(45, 10, 10, sda=True)
		sda_wp5 = mp_geo.Waypoint(55, 10, 10, sda=True)

		path_0 = []
		path_1 = [sda_wp1]
		path_2 = [sda_wp2, sda_wp3]
		path_3 = [sda_wp1, sda_wp2, sda_wp3, sda_wp4] 

		self.sda_engine.update_path_to_wp_at_index(path_0, 1)

		self.assertTrue(all(a == b for a,b in zip(init_wplist, self.sda_engine.wplist)))
		self.assertTrue(len(self.sda_engine.wplist) == init_wplist_len)	

		self.sda_engine.update_path_to_wp_at_index(path_1, 1)

		self.assertEqual(sda_wp1, self.sda_engine.wplist[1])
		self.assertTrue(len(self.sda_engine.wplist) == 1 + init_wplist_len)	

		self.sda_engine.update_path_to_wp_at_index(path_2, 1)

		self.assertTrue(len(self.sda_engine.wplist) == 2 + init_wplist_len)	
		self.assertEqual(sda_wp3, self.sda_engine.wplist[2])
		self.assertEqual(sda_wp2, self.sda_engine.wplist[1])


if __name__ == '__main__':
    unittest.main()
