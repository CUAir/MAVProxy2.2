#!/usr/bin/env python

'''WARNING: THIS FILE WAS MADE TO TEST SERVER V1

TESTS LIKELY NO LONGER WORK ON v3'''



import requests
import unittest
import json
import time


def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def isInteger(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def isString(string):
    return type(string) == type("Dummy string") or type(string) == type(unicode("dummy string"))


def isBool(string):
    return (string in ['True', 'true', 't', 'TRUE', 'T', True]) or (string in ['False', 'false', 'f', 'FALSE', 'F', False])


baseurl = 'http://localhost:8001'


""" Error messages for known bugs and errors """ 

waypointDictErrorMessage = ("Request is not instance of a list and is most likely an instance of a dict." +
"\nNOTE: If this is the case, this is an error in Groundstation v1." +  
"\nThis has been documented and should be changed.")


class Test_Status(unittest.TestCase):

    url = baseurl + '/v1/status'

    def test_status(self):
        r = requests.get(self.url)
        ''' 21 is the number of fields returned by the server '''
        self.assertTrue(len(r.json()), 21)

    def test_attitude(self):
        r = requests.get(self.url + '/attitude')
        self.assertTrue(isFloat(r.json()['yaw']))
        self.assertTrue(isFloat(r.json()['pitch']))
        self.assertTrue(isFloat(r.json()['roll']))
        self.assertTrue(isFloat(r.json()['yawspeed']))
        self.assertTrue(isFloat(r.json()['pitchspeed']))
        self.assertTrue(isFloat(r.json()['rollspeed']))

    def test_armed(self):
        r = requests.get(self.url + '/armed')
        self.assertTrue(isBool(r.text))

    def test_flight_battery(self):
        r = requests.get(self.url + '/battery')
        self.assertTrue(isFloat(r.json()['pct']))
        self.assertTrue(isFloat(r.json()['voltage']))

    def test_link(self):
        r = requests.get(self.url + '/link')
        self.assertTrue(isBool(r.json()['gps_link']))
        self.assertTrue(isBool(r.json()['plane_link']))

    def test_time(self):
        '''System time on plane'''
        r = requests.get(self.url + '/time')
        self.assertTrue(isInteger(r.text))

    def test_gps(self):
        r = requests.get(self.url + '/gps')
        self.assertTrue(isFloat(r.json()['rel_alt']))
        self.assertTrue(isFloat(r.json()['asl_alt']))
        self.assertTrue(isFloat(r.json()['lat']))
        self.assertTrue(isFloat(r.json()['lon']))
        self.assertTrue(isFloat(r.json()['heading']))
        self.assertTrue(isFloat(r.json()['vx']))
        self.assertTrue(isFloat(r.json()['vy']))
        self.assertTrue(isFloat(r.json()['vz']))

    def test_airspeed(self):
        r = requests.get(self.url + '/airspeed')
        self.assertTrue(isInteger(r.json()['vx']))
        self.assertTrue(isInteger(r.json()['vy']))
        self.assertTrue(isInteger(r.json()['vz']))

    def test_wind(self):
        r = requests.get(self.url + '/wind')
        self.assertTrue(isInteger(r.json()['vx']))
        self.assertTrue(isInteger(r.json()['vy']))
        self.assertTrue(isInteger(r.json()['vz']))

    def test_throttle(self):
        r = requests.get(self.url + '/throttle')
        self.assertTrue(isInteger(r.text))
        
        throttle = int(r.text)
        self.assertTrue(throttle >= 0 and throttle <= 100)

    def test_wp_count(self):
        r = requests.get(self.url + '/wp_count')
        self.assertTrue(isInteger(r.text))

    def test_current_wp(self):
        r = requests.get(self.url + '/current_wp')
        self.assertTrue(isInteger(r.text))

    def test_mode(self):
        r = requests.get(self.url + '/mode')
        self.assertFalse(isFloat(r.text) or isBool(r.text) or isInteger(r.text))

    def test_hud(self): 
        r = requests.get(self.url + '/hud')
        self.assertTrue(isFloat(r.json()['airspeed']))
        self.assertTrue(isFloat(r.json()['groundspeed']))
        self.assertTrue(isInteger(r.json()['heading']))
        self.assertTrue(isInteger(r.json()['throttle']))
        self.assertTrue(isFloat(r.json()['alt']))
        self.assertTrue(isFloat(r.json()['climb']))

class Test_Status(unittest.TestCase):

    url = baseurl + '/ground/api/v3/status'

    def test_status(self):
        r = requests.get(self.url)
        ''' 21 is the number of fields returned by the server '''
        self.assertTrue(len(r.json()), 21)

    def test_attitude(self):
        r = requests.get(self.url + '/attitude')
        self.assertTrue(isFloat(r.json()['yaw']))
        self.assertTrue(isFloat(r.json()['pitch']))
        self.assertTrue(isFloat(r.json()['roll']))
        self.assertTrue(isFloat(r.json()['yawspeed']))
        self.assertTrue(isFloat(r.json()['pitchspeed']))
        self.assertTrue(isFloat(r.json()['rollspeed']))

    def test_armed(self):
        r = requests.get(self.url + '/armed')
        self.assertTrue(isBool(r.text))

    def test_flight_battery(self):
        r = requests.get(self.url + '/battery')
        self.assertTrue(isFloat(r.json()['pct']))
        self.assertTrue(isFloat(r.json()['voltage']))

    def test_link(self):
        r = requests.get(self.url + '/link')
        self.assertTrue(isBool(r.json()['gps_link']))
        self.assertTrue(isBool(r.json()['plane_link']))

    def test_time(self):
        '''System time on plane'''
        r = requests.get(self.url + '/time')
        self.assertTrue(isInteger(r.text))

    def test_gps(self):
        r = requests.get(self.url + '/gps')
        self.assertTrue(isFloat(r.json()['rel_alt']))
        self.assertTrue(isFloat(r.json()['asl_alt']))
        self.assertTrue(isFloat(r.json()['lat']))
        self.assertTrue(isFloat(r.json()['lon']))
        self.assertTrue(isFloat(r.json()['heading']))
        self.assertTrue(isFloat(r.json()['vx']))
        self.assertTrue(isFloat(r.json()['vy']))
        self.assertTrue(isFloat(r.json()['vz']))

    def test_airspeed(self):
        r = requests.get(self.url + '/airspeed')
        self.assertTrue(isInteger(r.json()['vx']))
        self.assertTrue(isInteger(r.json()['vy']))
        self.assertTrue(isInteger(r.json()['vz']))

    def test_wind(self):
        r = requests.get(self.url + '/wind')
        self.assertTrue(isInteger(r.json()['vx']))
        self.assertTrue(isInteger(r.json()['vy']))
        self.assertTrue(isInteger(r.json()['vz']))

    def test_throttle(self):
        r = requests.get(self.url + '/throttle')
        self.assertTrue(isInteger(r.text))
        
        throttle = int(r.text)
        self.assertTrue(throttle >= 0 and throttle <= 100)

    def test_wp_count(self):
        r = requests.get(self.url + '/wp_count')
        self.assertTrue(isInteger(r.text))

    def test_current_wp(self):
        r = requests.get(self.url + '/current_wp')
        self.assertTrue(isInteger(r.text))

    def test_mode(self):
        r = requests.get(self.url + '/mode')
        self.assertFalse(isFloat(r.text) or isBool(r.text) or isInteger(r.text))

    def test_hud(self): 
        r = requests.get(self.url + '/hud')
        self.assertTrue(isFloat(r.json()['airspeed']))
        self.assertTrue(isFloat(r.json()['groundspeed']))
        self.assertTrue(isInteger(r.json()['heading']))
        self.assertTrue(isInteger(r.json()['throttle']))
        self.assertTrue(isFloat(r.json()['alt']))
        self.assertTrue(isFloat(r.json()['climb']))



class Test_WP_Functionality(unittest.TestCase):

    url = baseurl + '/v1/wp'
    url3 = baseurl + '/ground/api/v3/wp'

    def test_wp_add_get(self):
        payload = {"lat": "22", "lon": "33", "alt": "807", "command": 16, "index": -1}
        headers = {'Content-type': 'application/json'}
        r = requests.post(self.url,
                      data=json.dumps(payload), headers=headers)

        self.assertTrue(r)
        # Let wp_num have time to update
        time.sleep(2)
        countReq = requests.get(baseurl + '/ground/api/v3/status/wp_count')
        wpNum = int(countReq.text)-1

        wpReq = requests.get(self.url + '?wpnum=' + str(wpNum))
        self.assertEqual(wpReq.json()["alt"], 807.0)
        self.assertEqual(wpReq.json()["lon"], 33.0)
        self.assertEqual(wpReq.json()["lat"], 22.0)

        wpReq = requests.get(self.url)
        
        self.assertFalse(isinstance(wpReq.json(), dict), waypointDictErrorMessage)
        self.assertTrue(isinstance(wpReq.json(), list))
        self.assertEqual(wpReq.json()[wpNum]["alt"], 807.0)
        self.assertEqual(wpReq.json()[wpNum]["lon"], 33.0)
        self.assertEqual(wpReq.json()[wpNum]["lat"], 22.0)

    def test_wp_delete(self):

        # Make sure there is at least one waypoint
        payload = {"lat": "22", "lon": "33", "alt": "803", "command": 16, "index": -1}
        headers = {'Content-type': 'application/json'}
        r = requests.post(self.url,
                          data=json.dumps(payload), headers=headers)

        # Let wp_num have time to update
        time.sleep(2)

        r = requests.get(baseurl + '/ground/api/v3/status/wp_count')
        num = int(r.text)

        # remove all waypoints
        for x in range(0, num):
            r = requests.delete(self.url + '?wpnum=0')
            self.assertTrue(r)
            time.sleep(2)

        r = requests.get(baseurl + '/ground/api/v3/status/wp_count')
        self.assertTrue(int(r.text) == 0)

    def test_wp_insert(self):

        initial_wp_count = requests.get(baseurl + '/ground/api/v3/status/wp_count').text

        payload = {"lat": 22, "lon": 33, "alt": 711, "command": 16, "current": 0, "index": 0}
        headers = {'Content-type': 'application/json'}
        r = requests.post(self.url,
                          data=json.dumps(payload), headers=headers)


        time.sleep(2)
        payload = {"lat": 22, "lon": 33, "alt": 802, "command": 16, "index": -1}
        r = requests.post(self.url,
                          data=json.dumps(payload), headers=headers)

        time.sleep(2)
        payload = {"lat": 8, "lon": 8, "alt": 888, "command": 16, "index": 1}
        r = requests.post(self.url,
                          data=json.dumps(payload), headers=headers)
 
        # Let wp_num have time to update
        time.sleep(2)
        r = requests.get(baseurl + '/v1/status/wp_count')
        r2 = requests.get(baseurl + '/ground/api/v3/status/wp_count')
        r = requests.get(baseurl + '/v1/status/wp_count')
        self.assertEqual(int(r.text), 3 + int(initial_wp_count))

        r = requests.get(self.url + '?wpnum=1')

        self.assertEqual(r.json()["alt"], 888.0)
        self.assertEqual(r.json()["lon"], 8.0)
        self.assertEqual(r.json()["lat"], 8.0)

    def test_update_wp(self):
        # Make sure there is at least one waypoint
        payload = {"lat": 22, "lon": 33, "alt": 801, "command": 16, "current": 0, "index": 0}
        headers = {'Content-type': 'application/json'}
        r = requests.post(self.url,
                          data=json.dumps(payload), headers=headers)

        time.sleep(2)

        # Update Waypoint
        payload = {"lat": 123, "lon": 55, "alt": 908, "index": 0, "command": 16, "current": 1}
        r = requests.put(self.url,
                         data=json.dumps(payload), headers=headers)

        time.sleep(2)

        # Check updated waypoint
        r = requests.get(self.url + '?wpnum=0')
        self.assertEqual(r.json()["alt"], 908.0)
        self.assertEqual(r.json()["lon"], 55.0)
        self.assertEqual(r.json()["lat"], 123.0)

        # Clean up (delete waypoints)
        r = requests.get(baseurl + '/ground/api/v3/status/wp_count')
        num = int(r.text)
        for x in range(0, num):
            r = requests.delete(self.url + '?wpnum=0')
            self.assertFalse(isinstance(r.json(), dict), waypointDictErrorMessage)
            time.sleep(.5)


####################################################################################
############################ AUTH ##################################################
####################################################################################
    def test_wp_add_get(self):
            payload = {"lat": "22", "lon": "33", "alt": "807", "command": 16, "index": -1}
            headers = {'Content-type': 'application/json', 'token': 'aeolus'}
            r = requests.post(self.url3,
                          data=json.dumps(payload), headers=headers)

            self.assertTrue(r)
            # Let wp_num have time to update
            time.sleep(2)
            countReq = requests.get(baseurl + '/ground/api/v3/status/wp_count')
            wpNum = int(countReq.text)-1

            wpReq = requests.get(self.url3 + '?wpnum=' + str(wpNum))
            self.assertEqual(wpReq.json()["alt"], 807.0)
            self.assertEqual(wpReq.json()["lon"], 33.0)
            self.assertEqual(wpReq.json()["lat"], 22.0)

            wpReq = requests.get(self.url)
            
            self.assertFalse(isinstance(wpReq.json(), dict), waypointDictErrorMessage)
            self.assertTrue(isinstance(wpReq.json(), list))
            self.assertEqual(wpReq.json()[wpNum]["alt"], 807.0)
            self.assertEqual(wpReq.json()[wpNum]["lon"], 33.0)
            self.assertEqual(wpReq.json()[wpNum]["lat"], 22.0)

    def test_wp_delete(self):

            # Make sure there is at least one waypoint
            payload = {"lat": "22", "lon": "33", "alt": "803", "command": 16, "index": -1}
            headers = {'Content-type': 'application/json', 'token': 'aeolus'}
            r = requests.post(self.url3,
                              data=json.dumps(payload), headers=headers)

            # Let wp_num have time to update
            time.sleep(2)

            r = requests.get(baseurl + '/ground/api/v3/status/wp_count')
            num = int(r.text)

            # remove all waypoints
            for x in range(0, num):
                r = requests.delete(self.url + '?wpnum=0')
                self.assertTrue(r)
                time.sleep(2)

            r = requests.get(baseurl + '/ground/api/v3/status/wp_count')
            self.assertTrue(int(r.text) == 0)

    def test_wp_insert(self):

            initial_wp_count = requests.get(baseurl + '/ground/api/v3/status/wp_count').text

            payload = {"lat": 22, "lon": 33, "alt": 711, "command": 16, "current": 0, "index": 0}
            headers = {'Content-type': 'application/json', 'token': 'aeolus'}
            r = requests.post(self.url3,
                              data=json.dumps(payload), headers=headers)


            time.sleep(2)
            payload = {"lat": 22, "lon": 33, "alt": 802, "command": 16, "index": -1}
            r = requests.post(self.url3,
                              data=json.dumps(payload), headers=headers)

            time.sleep(2)
            payload = {"lat": 8, "lon": 8, "alt": 888, "command": 16, "index": 1}
            r = requests.post(self.url3,
                              data=json.dumps(payload), headers=headers)
     
            # Let wp_num have time to update
            time.sleep(2)
            r = requests.get(baseurl + '/v1/status/wp_count')
            r2 = requests.get(baseurl + '/ground/api/v3/status/wp_count')
            r = requests.get(baseurl + '/v1/status/wp_count')
            self.assertEqual(int(r.text), 3 + int(initial_wp_count))

            r = requests.get(self.url3 + '?wpnum=1')

            self.assertEqual(r.json()["alt"], 888.0)
            self.assertEqual(r.json()["lon"], 8.0)
            self.assertEqual(r.json()["lat"], 8.0)

    def test_update_wp(self):
            # Make sure there is at least one waypoint
            payload = {"lat": 22, "lon": 33, "alt": 801, "command": 16, "current": 0, "index": 0}
            headers = {'Content-type': 'application/json', 'token': 'aeolus'}
            r = requests.post(self.url3,
                              data=json.dumps(payload), headers=headers)

            time.sleep(2)

            # Update Waypoint
            payload = {"lat": 123, "lon": 55, "alt": 908, "index": 0, "command": 16, "current": 1}
            r = requests.put(self.url3,
                             data=json.dumps(payload), headers=headers)

            time.sleep(2)

            # Check updated waypoint
            r = requests.get(self.url3 + '?wpnum=0')
            self.assertEqual(r.json()["alt"], 908.0)
            self.assertEqual(r.json()["lon"], 55.0)
            self.assertEqual(r.json()["lat"], 123.0)

            # Clean up (delete waypoints)
            r = requests.get(baseurl + '/ground/api/v3/status/wp_count')
            num = int(r.text)
            for x in range(0, num):
                r = requests.delete(self.url + '?wpnum=0')
                self.assertFalse(isinstance(r.json(), dict), waypointDictErrorMessage)
                time.sleep(.5)




class Test_Other_Functionaltiy(unittest.TestCase):

    url = baseurl + '/v1'
    url3 = baseurl + '/ground/api/v3'

    def test_change_mode(self):

        testMode = "AUTO"

        payload = {"mode": testMode}
        headers = {'Content-type': 'application/json'}

        
        r = requests.post(self.url + '/set_mode',
                     data=json.dumps(payload), headers=headers)
        self.assertEqual(r.text,"Accepted mode change")
        time.sleep(2)
        r = requests.get(self.url + '/flight_mode')
        self.assertEqual(r.text, testMode)

        # Change mode a second time to confim that mode changed and
        # did not just start in 'AUTO'

        testMode = "MANUAL"

        payload = {"mode": testMode}
        headers = {'Content-type': 'application/json'}

        r = requests.post(self.url + '/set_mode',
                     data=json.dumps(payload), headers=headers)
        self.assertEqual(r.text,"Accepted mode change")
        time.sleep(2)
        r = requests.get(self.url + '/flight_mode')
        self.assertEqual(r.text, testMode)

    def test_change_mode_auth(self):
        time.sleep(6)
        testMode = "CIRCLE"

        payload = {"mode": testMode}
        headers = {'Content-type': 'application/json', 'token': 'aeolus'}

        r = requests.post(self.url3 + '/set_mode',
                     data=json.dumps(payload), headers=headers)
        self.assertEqual(r.text,"Accepted mode change")
        time.sleep(2)
        r = requests.get(self.url3 + '/flight_mode')
        self.assertEqual(r.text, testMode)

        # Change mode a second time to confim that mode changed and
        # did not just start in 'AUTO'

        testMode = "LAND"

        payload = {"mode": testMode}
        headers = {'Content-type': 'application/json', 'token': 'aeolus'}

        r = requests.post(self.url3 + '/set_mode',
                     data=json.dumps(payload), headers=headers)
        self.assertEqual(r.text,"Accepted mode change")
        time.sleep(2)
        r = requests.get(self.url3 + '/flight_mode')
        self.assertEqual(r.text, testMode)

'''class Test_Other_Functionaltiy(unittest.TestCase):
    url3 = baseurl + '/ground/api/v3/geofence'

    def test_post_get(self):
        payload = [{"lat": 5, 'lon': 5}, {'lat': 10, 'lon':'10'}]
        headers = {'Content-type': 'application/json', 'token': 'aeolus'}

        r = requests.post(self.url3,
                     data=json.dumps(json.dumps(payload)), headers=headers)
        self.assertEquals(r.text, "Added Fence")

        r = requests.get(self.url3)
        '''
        #CHECK GETTING FENCE HERE


if __name__ == '__main__':
    unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()