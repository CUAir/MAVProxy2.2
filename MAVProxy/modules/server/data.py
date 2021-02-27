#!/usr/bin/env python
from collections import deque
import pickle



class Data():
    password = 'aeolus'

    pdata = {'FLIGHT_MODE':"MAV", 'INFO_TEXT': None, 'WARNING_TEXT': None, 'ERROR_TEXT': None}

    # wayponint data
    wplist = []
    sda_wplist = []
    twp = []
    json = {}
    wpcommand = ""  # add, remove, edit, move
    wpNum = -1

    # mode change data
    mode = ""  # Available modes:'RTL', 'TRAINING', 'LAND', 'AUTOTUNE', 'STABILIZE', 'AUTO', 'GUIDED', 'LOITER', 'MANUAL', 'FBWA', 'FBWB', 'CRUISE', 'INITIALISING', 'CIRCLE', 'ACRO'

    # arm disarm data
    needArm = False
    needDisarm = False

    armed = False
    safe = False

    # GPS LOCk
    have_gps_lock = False

    # parameter data
    params = {}
    parameterToUpdate = ''
    valueToUpdate = ''
    max_param_num = 0

    # current waypoint functionality
    currentWPIndex = -1
    wp_seq = -1

    # for interop
    # pdata['server_info'].server_time = 0
    pdata['server_info'] = {}
    try:
        d = pickle.load( open( "interop_url_data.pickle", "rb" ) )
        interop_url = d['url']
        interop_username = d['username']
        interop_password = d['password']
        interop_mission_id = d['mission_id']
    except:
        interop_url = 'http://10.42.0.1:8000'
        interop_username = 'cuairsim'
        interop_password = 'aeolus'

    # (deque1, deque2, deque3...) where each deque contains [{lat:lat, lon:lon, alt:alt, time:time},...]
    obstacle_history = None

    # for geofences
    fenceJSON = {}

    # Signals interop server has been started
    server_active = False
    interop_working = True

    #
    database = "database.db"
    # when searching for closest time look for times plus or minus this number of seconds
    dbTimeVariance = 10.0

    powerboardSite = 'http://localhost:5001'
    powerboard = {}

    # new statuses

    num_sats = -1
    flight_time = -1
    sensor_status = {}
    ekf_status = "UNKNOWN"
    hw_status = -1
    power_status = "UNKNOWN"
    Vcc = -1
    Vservo = -1
    radio_status = {}
    alt_error = -1
    airspeed_error = -1


    
