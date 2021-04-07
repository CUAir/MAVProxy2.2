import unittest
import numpy as np
import modules.lib.mp_geometry as mp_geo
import time
import sda_pdriver

class SDAtestpdriver (unittest.TestCase):
   
    def test_generate_static(self):

        model = sda_pdriver.ProbModelStatic()
        stat_pos = np.array([100, 150, 200])
        stat_obst = mp_geo.StationaryObstacle(20, stat_pos)

        lst={"stationary":[stat_obst]}

        eval_list=lst["stationary"]

        geofence_points = [(0,0), (0, 400), (400, 400), (400, 0)]
        geofence = mp_geo.Geofence(geofence_points)

        model.generate(lst,geofence)

        self.assertEqual(eval_list, model.obstacles)
        self.assertEqual(geofence, model.geofences)

    def test_get_prob_static(self):

        model = sda_pdriver.ProbModelStatic()
        stat_pos1 = np.array([100, 150, 200])
        stat_obst1 = mp_geo.StationaryObstacle(20, stat_pos1)

        stat_pos2 = np.array([50, 350, 120])
        stat_obst2 = mp_geo.StationaryObstacle(45, stat_pos2)

        lst={"stationary":[stat_obst1, stat_obst2]}
        eval_list=lst["stationary"]
        model.obstacles=eval_list
        
        geofence_points = [(0,0), (0, 400), (400, 400), (400, 0)]
        geofence = mp_geo.Geofence(geofence_points)
        model.geofences=geofence

        pos0 = np.array([100, 100, 80])
        pos1 = np.array([100, 150, 100])
        pos2 = np.array([120, 100, 80])
        pos3 = np.array([100, 440, 80])
        pos4 = np.array([12,   13, 14])

        test1=model.get_prob(pos0[0],pos0[1],pos0[2],0)
        test2=model.get_prob(pos1[0],pos1[1],pos1[2],2)
        test3=model.get_prob(pos2[0],pos2[1],pos2[2],0)
        test4=model.get_prob(pos3[0],pos3[1],pos3[2],11)
        test5=model.get_prob(pos4[0],pos4[1],pos4[2],5)

        self.assertEqual(0, test1)
        self.assertEqual(1, test2)
        self.assertEqual(1, test3)
        self.assertEqual(1, test4)
        self.assertEqual(0, test5)


    def test_generate_expand(self):

        model = sda_pdriver.ProbModelExpand()
        stat_pos = np.array([100, 150, 200])
        stat_obst = mp_geo.StationaryObstacle(20, stat_pos)

        lst={"stationary":[stat_obst]}

        eval_list=lst["stationary"]

        geofence_points = [(0,0), (0, 400), (400, 400), (400, 0)]
        geofence = mp_geo.Geofence(geofence_points)

        model.generate(lst,geofence)

        self.assertEqual(eval_list, model.obstacles)
        self.assertEqual(geofence, model.geofences)

    def test_get_prob_expand(self):

        model = sda_pdriver.ProbModelExpand()

        stat_pos1 = np.array([100, 150, 200])
        stat_obst1 = mp_geo.StationaryObstacle(20, stat_pos1)

        stat_pos2 = np.array([50, 350, 120])
        stat_obst2 = mp_geo.StationaryObstacle(45, stat_pos2)

        lst={"stationary":[stat_obst1, stat_obst2]}
        eval_list=lst["stationary"]
        model.obstacles=eval_list
        
        geofence_points = [(0,0), (0, 400), (400, 400), (400, 0)]
        geofence = mp_geo.Geofence(geofence_points)
        model.geofences=geofence


        pos0 = np.array([100, 100, 80])
        pos1 = np.array([100, 150, 100])
        pos2 = np.array([120, 100, 80])
        pos3 = np.array([100, 440, 80])
        pos4 = np.array([12,   13, 14])

        test1=model.get_prob(pos0[0],pos0[1],pos0[2],0)
        test2=model.get_prob(pos1[0],pos1[1],pos1[2],2)
        test3=model.get_prob(pos2[0],pos2[1],pos2[2],0)
        test4=model.get_prob(pos3[0],pos3[1],pos3[2],11)
        test5=model.get_prob(pos4[0],pos4[1],pos4[2],5)

        self.assertEqual(0, test1)
        self.assertEqual(1, test2)
        self.assertEqual(1, test3)
        self.assertEqual(1, test4)
        self.assertEqual(0, test5)

    def test_generate_LinearInterp(self):

        model = sda_pdriver.ProbModelLinearInterp()
        stat_pos = np.array([100, 150, 200])
        stat_obst = mp_geo.StationaryObstacle(20, stat_pos)

        lst={"stationary":[stat_obst]}

        eval_list=lst["stationary"]

        geofence_points = [(0,0), (0, 400), (400, 400), (400, 0)]
        geofence = mp_geo.Geofence(geofence_points)

        model.generate(lst,geofence)

        self.assertEqual(eval_list, model.obstacles)
        self.assertEqual(geofence, model.geofences)


    def test_get_prob_LinearInterp(self):

        model=sda_pdriver.ProbModelLinearInterp()
        stat_pos1 = np.array([100, 150, 200])
        stat_obst1 = mp_geo.StationaryObstacle(20, stat_pos1)

        stat_pos2 = np.array([50, 350, 120])
        stat_obst2 = mp_geo.StationaryObstacle(45, stat_pos2)

        lst={"stationary":[stat_obst1, stat_obst2]}
        eval_list=lst["stationary"]
        model.obstacles=eval_list
        
        geofence_points = [(0,0), (0, 400), (400, 400), (400, 0)]
        geofence = mp_geo.Geofence(geofence_points)
        model.geofences=geofence


        pos0 = np.array([100, 100, 80])
        pos1 = np.array([100, 150, 100])
        pos2 = np.array([120, 100, 80])
        pos3 = np.array([100, 440, 80])
        pos4 = np.array([12,   13, 14])
        test1=model.get_prob(pos0[0],pos0[1],pos0[2],0)
        test2=model.get_prob(pos1[0],pos1[1],pos1[2],2)
        test3=model.get_prob(pos2[0],pos2[1],pos2[2],0)
        test4=model.get_prob(pos3[0],pos3[1],pos3[2],11)
        test5=model.get_prob(pos4[0],pos4[1],pos4[2],5)

        print test1
        print test2
        print test3
        print test4
        print test5
        
        self.assertEqual(0, test1)
        self.assertEqual(1, test2)
        self.assertEqual(0, test3)
        self.assertEqual(1, test4)
        self.assertEqual(0, test5)


if __name__ == '__main__':
    unittest.main()
    
