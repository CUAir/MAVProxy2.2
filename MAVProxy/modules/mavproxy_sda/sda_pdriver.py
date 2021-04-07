import numpy as np 
import modules.lib.mp_geometry as mp_geo
import time

class ProbModel(object):
    def __init__(self):
        self.obstacles = []
        self.geofence = None

    def generate(self, obstacles, geofence):
        raise NotImplementedError()

    def get_prob(self, x, y, z, t):
        raise NotImplementedError()

    def print_obst(self):
        if len(self.obstacles) == 0:
            return "no obstacles to print"
        try: 
            obsts = ''
            for obstacle in self.obstacles:
                obsts += (str(obstacle) + '\n')
            return obsts
        except Exception as e:
            print (e) 


class ProbModelStatic(ProbModel):
    def __init__(self):
        self.obstacles = []
        self.geofences = None

    def generate(self, obstacles, geofence=None):
        self.obstacles = obstacles
        self.geofences = geofence

    def get_prob(self, x, y, z, t):
        p = mp_geo.Point(x, y, z)
        
        for ob in self.obstacles:
            if(ob.distance(p) < ob.radius):
                return 1
        #there should be a geofence
        if self.geofences != None:
            if not(self.geofences.contains(p.x,p.y)):
                return 1
        return 0

class ProbModelExpand(ProbModel):
    def __init__(self):
        self.obstacles = []
        self.geofences = None

    def generate(self, obst, geofence = None):
        self.obstacles = obst
        self.geofences = geofence
    
    def get_prob(self, x, y, z, t):
        p = mp_geo.Point(x, y, z)
        for ob in self.obstacles:
            if isinstance(ob,mp_geo.StationaryObstacle):
                if ob.distance(p) < ob.radius:
                    return 1
        #should have a geofence
        if self.geofences != None:
            if not (self.geofences.contains(p.x,p.y)):
                return 1 
        return 0

class ProbModelLinearInterp(ProbModel):
    
    def __init__(self):
        self.obstacles = []
        self.geofences = None

    def generate(self, obstacles, geofence = None):
        self.obstacles = obstacles
        self.geofences = geofence

    def get_prob(self, x, y, z, t):
        p = mp_geo.Point(x, y, z)
        #geofence should exist, if not uses short circuit evaluation to prevent error
        if self.geofences != None: 
            if not self.geofences.contains(p.x,p.y):
                return 1 
        for ob in self.obstacles:
            if isinstance(ob, mp_geo.StationaryObstacle):
                if ob.distance(p) < ob.radius:
                    return 1
        return 0

class ProbDriver:
    def __init__(self, history_length=50, model=ProbModelStatic(), geofence=None):
        self.history_length = history_length
        self.stat_obstacles = []
        self.current_model = model
        self.convert = mp_geo.convert_instance
        self.geofences = geofence

    def generate_model(self):
        self.current_model.generate(self.stat_obstacles, geofence=self.geofences)

    def get_model(self):
        return self.current_model

    def add_stat_obst(self, stat_obst):
        if isinstance(stat_obst, mp_geo.StationaryObstacle):
            self.stat_obstacles.append(stat_obst)
        else: 
            raise ValueError("object is not of type Stationary Obstacle. Note this function is for testing only")

    # s_obs is obstacle data directly from the interop server.
    def update_stationary_obstacles(self, s_obs):
        new_stat_obstacles = []
        for i, obst in enumerate(s_obs):
            obst_xy = self.convert.ll2m(obst['latitude'], obst['longitude'])
            obst_xyz = np.array([obst_xy[0], obst_xy[1], obst['cylinder_height']])
            new_stat_obstacles.append(mp_geo.StationaryObstacle(obst['cylinder_radius'], obst_xyz)) 
        self.stat_obstacles = new_stat_obstacles

    # m_obs is obstacles data directly from the interop server.

    def update_obstacles(self, m_obst, s_obst):
        self.update_stationary_obstacles(s_obst)
        self.generate_model()

    def update_obstacles_from_interop(self, obstacles):
        s_obst = obstacles['stationary_obstacles']
        self.update_obstacles(s_obst)

    def set_geofence(self, geo_f):
        if isinstance(geo_f,mp_geo.Geofence):
            if self.current_model == None:
                raise ValueError("current model not implemented")
            self.current_model.geofence = geo_f
        else:
            raise TypeError("Bad type!: " + str(type(geo_f)))

    """ things that still need to be done:
        Change the lists for moving obstacle history to deques 
        add geofences to the prob model drivers and add geofences to the prob models themselves
        have prob models check against geofence 
        see the prob model integrated into mavproxy 
        integrate prob models into RRTs """
        
