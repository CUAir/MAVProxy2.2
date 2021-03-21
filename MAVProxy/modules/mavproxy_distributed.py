#!/usr/bin/env python
import requests
import os
import json
import traceback
from hashlib import md5

from modules.lib import mp_module

import mavproxy_logging
logger = mavproxy_logging.create_logger("distributed")

instance = None
SERVER_TIMEOUT = 5  # in seconds


class Distributed(mp_module.MPModule):
    def __init__(self, mpstate):
        super(Distributed, self).__init__(mpstate, "distributed", "Distributed Systems Module", public=True)
        self.add_command('ds_images', self._print_metadata, "show distributed systems image data")
        self.add_command('ds_status', self._cmd_status, "show distributed systems connection status")
        self.add_command('ds_start', self.cmd_start, "start distributed systems connection")
        self.add_command('ds_point_gimbal', self._cmd_point_gimbal, "point the gimbal at specified lat and lon")
        self.add_command('ds_reset_gimbal', self._cmd_reset_gimbal, "reset the gimbal to default state")
        self.add_command('ds_land', self._cmd_landing, "send landing notification")
        self.add_command('ds', self._print_help, "shows a help message for using the interop command line")
        self.add_command('ds_regions', self._print_regions, "shows distributed system's regions of interest")

        self.session = None
        self.gimbal_mode = None
        self.distributed_url = None
        self.distributed_username = None
        self.distributed_password = None
        self.image_data = []
        self.header = None
        self.priority_regions = None
        self.adlc_targets = None
        self.is_active = False
        self.airdrop = None

    def cmd_start(self, args):
        return self.start(False, *args)

    def start(self, is_hashed, d_url='http://192.168.0.22:9000', d_username='Autopilot', d_password='aeolus', from_file=True):
        self.session = requests.Session()
        filepath = self.get_server_file()
        if not is_hashed:
            if not d_url.startswith("http://"):
                logger.error("First argument must be url with http:// and have a port")
            self.distributed_url = d_url
            self.distributed_username = d_username
            m = md5()
            m.update(d_password)
            self.distributed_password = m.hexdigest()
        elif from_file:
            try:
                with open(filepath, "r") as login_file:
                    json_string = login_file.read()
                    unicode_json = json.loads(json_string)
                    self.distributed_url = unicode_json[u'url']
                    self.distributed_username = unicode_json[u'username']
                    self.distributed_password = unicode_json[u'password']
            except (IOError, ValueError):
                self.distributed_url = 'http://192.168.0.22:9000'
                self.distributed_username = 'Autopilot'
                self.distributed_password = 'aeolus'
        else:
            self.distributed_url = d_url
            self.distributed_username = d_username
            self.distributed_password = d_password
        try:
            with open(filepath, 'w') as output_file:
                output_json = json.dumps({
                    'url': self.distributed_url,
                    'username': self.distributed_username,
                    'password': self.distributed_password
                })
                output_file.write(output_json)
        except IOError:
            logger.error('Unable to write to output file')

        # Get auth token - also tests if the connection worked
        try:
            auth_headers = {"Authorization": self.distributed_password, "Username": self.distributed_username}
            auth_data = self.session.get(self.distributed_url + "/api/v1/auth", headers=auth_headers, timeout=SERVER_TIMEOUT)
        except Exception:
            logger.error("Failed to start distributed server. url: {}".format(self.distributed_url))
            logger.error(traceback.format_exc())
            return False
        if auth_data.status_code != 200:
            logger.error("Failed to start distributed server url: {}".format(self.distributed_url))
            logger.error("Error: " + str(auth_data.status_code))
            return False
        self.header = {'X-AUTH-TOKEN': json.loads(auth_data.text)["token"]}
        self.is_active = True
        self.get_all_info()
        logger.info("Connection to " + str(self.distributed_url) + " established.")
        return True

    def get_all_info(self):
        if self.session is None:
            return
        self._get_targets()
        self._get_gimbal_settings()
        self._get_priority_regions_from_server()
        self._get_adlc_from_server()

    def _get_targets(self):
        image_data = self.session.get(self.distributed_url + "/api/v1/image/geotag", headers=self.header)
        try:
            image_data = json.loads(image_data.text)
            image_data = map(lambda x: x[1], sorted(image_data.iteritems()))
            image_data = filter(lambda x: x is not None, image_data)
            final_image_data = []
            for item in image_data:
                new_item = []
                new_item['imageUrl'] = item['url']
                for corner in ['topLeft', 'bottomLeft', 'bottomRight', 'topRight']:
                    new_item[corner]['lat'] = item[corner]['latitude']
                    new_item[corner]['lon'] = item[corner]['longitude']
            self.image_data = final_image_data
        except Exception:
            logger.error(traceback.format_exc())

    def _get_gimbal_settings(self):
        gimbal_data = self.session.get(self.distributed_url + "/api/v1/settings/gimbal/recent", headers=self.header)
        no_gimbal_settings = 'No GimbalSettings in database'
        if gimbal_data.text == no_gimbal_settings or gimbal_data.status_code == 204:
            return
        if gimbal_data.status_code != 200:
            logger.error("DISTRIBUTED SERVER ERROR " + str(gimbal_data.status_code))
            return

        try:
            self.gimbal_mode = gimbal_data.json()['mode']
        except Exception:
            logger.error(traceback.format_exc())

    def _get_priority_regions_from_server(self):
        try:
            regions = self.session.get(self.distributed_url + "/api/v1/roi/mdlc", headers=self.header)
            regions = json.loads(regions.text)
            self.priority_regions = regions
        except Exception:
            logger.error(traceback.format_exc())

    def _get_adlc_from_server(self):
        try:
            targets = self.session.get(self.distributed_url + "/api/v1/roi/adlc", headers=self.header)
            targets = json.loads(targets.text)
            self.adlc_targets = targets
        except Exception:
            logger.error(traceback.format_exc())

    def _cmd_status(self, args):
        logger.info('Connected to distributed' if self.is_active else 'Not connected to distributed')

    def point_gimbal(self, latlon):
        data = {
            "mode": 'gps',
            "gps": {"latitude": latlon['lat'], "longitude": latlon['lon']}
        }

        if self.session is None:
            return False

        gimbal_result = self.session.post(self.distributed_url + "/api/v1/settings/gimbal", json=data, headers=self.header)
        return gimbal_result.status_code == 200


    def _cmd_point_gimbal(self, args):
        try:
            lat = float(args[0])
            lon = float(args[1])
        except (ValueError, IndexError):
            logger.error("Invalid args; need lat and lon")

        if self.point_gimbal({'lat': lat, 'lon': lon}):
            logger.info("Pointed successfully")
        else:
            logger.error("Error pointing gimbal")

    def reset_gimbal(self):
        data = {"mode": 'ground'}
        if self.session is None:
            return False

        gimbal_url = self.distributed_url + "/api/v1/settings/gimbal"
        gimbal_result = self.session.post(gimbal_url, json=data, headers=self.header)
        return gimbal_result.status_code == 200

    def set_camera_mode(self, data):
        if self.session is None:
            return False
        camera_url = self.distributed_url + "/api/v1/settings/camera_gimbal"
        camera_result = self.session.post(camera_url, json=data, headers=self.header)
        return gimbal_result.status_code

    def _cmd_reset_gimbal(self, args):
        if self.reset_gimbal():
            logger.info("Gimbal reset successfully")
        else:
            logger.error("Error resetting gimbal")

    def _cmd_landing(self, args):
        self.landing()

    def landing(self):
        logger.info("Signaling DS Landing")
        if self.session is None:
            logger.error("No distributed connection")
            return False

        landing_url = self.distributed_url + "/api/v1/landing"
        landing_result = self.session.post(landing_url, headers=self.header)
        if landing_result.status_code == 200:
            logger.info("DS landing sent successfully")
            return True
        else:
            logger.error("Error sending DS landing")
            return False

    def _print_metadata(self, args):
        if self.image_data:
            for i, img in enumerate(self.image_data):
                logger.info('Image ' + str(i) + ':')
                for key in img:
                    logger.info(key + ': ' + str(img[key]))
                print ('\n')
        else:
            logger.info('No image data')

    def _print_help(self, args):
        logger.info('usage: ["ds_images | ds_start <url> | ds_stop | ds_status | ds_point_gimbal <lat> <lon> | ds_reset_gimbal | ds_land | ds"]')

    def _print_regions(self, args):
        if self.priority_regions:
            logger.info('Priority Regions')
            for i, region in enumerate(self.priority_regions['high']):
                logger.info('Priority Region ' + str(i) + ':' + str(region['latitude']) + ', ' + str(region['longitude']))
        else:
            logger.info('No priority region data')

    def get_image_data(self):
        return self.image_data

    def get_priority_regions(self):
        return self.priority_regions if self.priority_regions is not None else {"high": [], "medium": [], "low": []}

    def get_adlc_targets(self):
        return self.adlc_targets if self.adlc_targets is not None else []

    def server_active(self):
        return self.is_active

    def airdrop_settings(self):
        return self.airdrop

    def get_server_file(self):
        return os.path.split(os.path.realpath(__file__))[0] + "/distributed_data.json"

    def get_mode(self):
        return self.gimbal_mode

#Not called TODO : use func to get rois if mod restarted during 2nd pass
    def get_rois(self):
        url = self.distributed_url + "/api/v1/roi"
        rois_res = self.session.get(url, headers=self.header)
        rois = json.loads(rois_res.text)
        roi_dict = {}
        for roi in rois:
            roi_dict[roi['id']] = roi
        return roi_dict

def get_distributed_mod():
    if instance is None:
        raise Exception("Distributed instance not yet initialized")
    return instance

def init(mpstate):
    global instance
    instance = Distributed(mpstate)
    return instance
