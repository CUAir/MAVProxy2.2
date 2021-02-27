// @flow

import $ from 'jquery';
import Ajv from 'ajv';

import { api } from 'js/constants/Sites';

import * as StatusActionCreator from 'js/actions/StatusActionCreator';
import * as InteropActionCreator from 'js/actions/InteropActionCreator';
import * as WaypointActionCreator from 'js/actions/WaypointActionCreator';
import * as CalibrationActionCreator from 'js/actions/CalibrationActionCreator';
import * as FenceActionCreator from 'js/actions/FenceActionCreator';
import * as SdaActionCreator from 'js/actions/SdaActionCreator';
import * as ParametersActionCreator from 'js/actions/ParametersActionCreator';
import * as SettingsActionCreator from 'js/actions/SettingsActionCreator';
import * as TargetImgActionCreator from 'js/actions/TargetImagesActionCreator';

// import GlobalStore from 'js/stores/GlobalStore';

import {
  assertJson, waypointsType, sdaType, fenceType,
  targetImgType, gimbalType
} from 'js/utils/TypeValidation';
import { statusSchema, interopSchema, splineSchema, regionSchema, airdropSchema } from 'js/utils/Schema';
import { alert } from 'js/utils/ComponentUtils';

const ajv = new Ajv();

/**
 * @module utils/ReceiveApi
 */

let receiverProcess;
let _non_urgent_update_counter = 0;
let _non_urgent_update_freq = 2;
let interopProcess;
let _mavproxy_up = true;
let _last_mav_info = '';
let _last_mav_warning = '';
let _last_mav_error = '';
let _historical = false;
let _last_invalid_time = 0;

const commandNumberTOword = {
  '0': 'MANUAL', '1': 'CIRCLE', '2': 'STABILIZE', '3': 'TRAINING', '4': 'ACRO',
  '5': 'FBWA', '6': 'FBWB', '7': 'CRUISE', '8': 'AUTOTUNE', '10': 'AUTO',
  '11': 'RTL', '12': 'LOITER', '15': 'GUIDED'
};


function assertValidResult(name, stringValue, type, time) {
  if (stringValue === 'null' && time != undefined && time !== _last_invalid_time) {
    _last_invalid_time = time;
    alert.error('Invalid time: please select another time');
  }
  return assertJson(name, stringValue, type);
}

function getParameters(time) {
  const data = time == undefined ? null : { tm: time };
  $.get({ url: api + 'params', data }).done(data => {
    const modeSwitchParam = JSON.parse(data)['FLTMODE1'];
    if (data !== 'No data' && data !== 'null' && data != undefined) {
      StatusActionCreator.receiveModeSwitch(commandNumberTOword[modeSwitchParam]);
    }
  });
}

export function getWaypoints(time) {
  const data = time == undefined ? null : { tm: time };
  $.get({ url: api + 'wp', data }).done(data => {
    if (assertValidResult('Waypoints', data, waypointsType, time)) {
      WaypointActionCreator.receiveWaypoints(JSON.parse(data));
    }
  });
}

function getCoverage(time) {
  const data = time == undefined ? null : { tm: time };
  $.get({ url: api + 'coverage', data: data }).done(data => {
    TargetImgActionCreator.receiveCoverage(JSON.parse(data));
  });
}

export function getSdaWaypoints(start_index: number, end_index: number) {
  const data = { start_index, end_index };
  if (start_index === -1 || end_index === -1) {
    alert.error('No SDA start and end points selected');
    return;
  }
  const timeout = ((end_index - start_index) * 6000);
  $.get({ url: api + 'wp/sda', timeout, data }).done(data => {
    if (assertValidResult('SdaWaypoints', data, waypointsType)) {
      WaypointActionCreator.receiveSdaWaypoints(JSON.parse(data));
    }
  });
}

function getSDA(time) {
  const data = time == undefined ? null : { tm: time };
  $.get({ url: api + 'sda', data }).done(data => {
    if (assertValidResult('SDA', data, sdaType, time)) {
      SdaActionCreator.receiveSdaEnabled(JSON.parse(data));
    }
  });
}

function getGeofences(time) { // eslint-disable-line no-unused-vars
  const data = time == undefined ? null : { tm: time };
  $.get({ url: api + 'geofence', data }).done(data => {
    if (assertValidResult('Geofence', data, fenceType, time)) {
      FenceActionCreator.receiveFencePoints(JSON.parse(data));
    }
  });
}

// function parseMovingObstaclePoint(point, obstacleIndex) {
//   const { interop } = GlobalStore.getState();
//   return {
//     time: point[0],
//     lat: point[1][0],
//     lon: point[1][1],
//     alt: point[1][2],
//     radius: interop.moving.get(obstacleIndex).get('sphere_radius')
//   };
// }

// function parseMovingObstaclePath(pathData, obstacleIndex) {
//   return {
//     period: pathData[0],
//     points: pathData[1].map(point => parseMovingObstaclePoint(point, obstacleIndex))
//   };
// }

// export function getMovingObstacles() {
//   $.get({url: api + 'sda_obst_state'}).done(data => {
//     let parsedJson = JSON.parse(data);
//     let obstacles = parsedJson.map(parseMovingObstaclePath);
//     SdaActionCreator.receiveMovingObstacles(obstacles);
//   });
// }

export function getCompetitionWaypoints() {
  $.ajax({
    url: api + 'interop/mission_waypoints',
    type: 'GET',
    contentType: 'application/json',
    success: (data) => {
      let parsedJson = JSON.parse(data);
      WaypointActionCreator.receiveCompetitionWaypoints(parsedJson);
    }
  });
}


/* Convert array from received JSON to PlanePathPoint object */
function parsePlanePathPoint(pointData) {
  return {
    time: pointData[0],
    lat: pointData[1][0],
    lon: pointData[1][1]
  };
}

export function getPlanePredictions() {
  $.get({ url: api + 'sda_plane_state' }).done(data => {
    let parsedJson = JSON.parse(data);
    let planePath = parsedJson.map(parsePlanePathPoint);
    SdaActionCreator.receivePlanePreditions(planePath);
  }).fail(function (jqXHR, textStatus, errorThrown) {
    alert.error('Plane Prediction: ' + errorThrown);
  });
}

function getTargetImg(time) {
  const data = time == undefined ? null : { tm: time };
  $.get({ url: api + 'distributed/target_data', data }).done(data => {
    if (data !== 'Error: Server is not active') {
      if (data == 'null') {
        return;
      }

      if (assertValidResult('TargetImg', data, targetImgType, time)) {
        TargetImgActionCreator.receiveTargetImg(JSON.parse(data));
      }
      TargetImgActionCreator.distributedActive(true);
    } else {
      TargetImgActionCreator.distributedActive(false);
    }
  });
}

function getGimbalStatus(time) {
  const data = time == undefined ? null : { tm: time };
  $.get({ url: api + 'distributed/gimbal', data }).done(data => {
    if (data !== 'Error: Server is not active' && data !== 'null') {
      if (assertValidResult('GimbalStatus', data, gimbalType, time)) {
        TargetImgActionCreator.distributedActive(true);
        InteropActionCreator.gimbalStatus(JSON.parse(data) === 'gps');
      }
    }
  });
}

function getProgress() {
  $.get({ url: api + 'status/progress' }).done(data => {
    var res = JSON.parse(data);
    if (res.time_to_landing != null) {
      StatusActionCreator.receiveTimeToLanding(res.time_to_landing);
    }
    if (res.percentage != null) {
      StatusActionCreator.receiveMissionPercent(res.percentage);
    }
  });
}

const statusValidate = ajv.compile(statusSchema);
const interopValidate = ajv.compile(interopSchema);
const splineValidate = ajv.compile(splineSchema);
const regionValidate = ajv.compile(regionSchema);
const airdropValidate = ajv.compile(airdropSchema);

function validateData(data, validator) {
  try {
    const parsed_data = JSON.parse(data);
    if (validator(parsed_data)) {
      return true;
    } else {
      console.log(validator.errors); // eslint-disable-line no-console
      console.log(parsed_data); // eslint-disable-line no-console
      return false;
    }
  } catch (err) {
    console.log(err); // eslint-disable-line no-console
  }
}

function getAirdrop(time) {
  const data = time == undefined ? null : { tm: time };
  $.get({ url: api + 'distributed/airdrop', data }).done(data => {
    if (data !== 'null' && validateData(data, airdropValidate)) {
      const { gpsTargetLocation } = JSON.parse(data);
      TargetImgActionCreator.receiveAirdropLocation(gpsTargetLocation.latitude, gpsTargetLocation.longitude);
    }
  });
}

function getStatusData(time) {
  const data = time == undefined ? null : { tm: time };
  $.get({ url: api + 'status', data }).done(data => {
    if (!_mavproxy_up) alert.success('Regained connection to MAVProxy backend');
    _mavproxy_up = true;
    StatusActionCreator.reconnect();

    if (validateData(data, statusValidate)) {
      const { airspeed, battery, attitude, link, armed, throttle, current_wp,
        mode, wind, gps, mav_info, mav_warning, mav_error, gps_status,
        signal, safe } = JSON.parse(data);
      if (airspeed !== null) {
        StatusActionCreator.receiveAirspeed(airspeed);
        StatusActionCreator.receiveClimbRate(airspeed.climb);
      }
      if (battery !== null) StatusActionCreator.receiveBattery(battery);
      if (attitude !== null) StatusActionCreator.receiveAttitude(attitude);
      if (link !== null) {
        StatusActionCreator.receiveGPSLink(link.gps_link);
        StatusActionCreator.receivePlaneLink(link.plane_link);
        StatusActionCreator.receiveLinkDetails(link.links);
      }
      if (armed !== null) StatusActionCreator.receiveArmed(armed);
      if (throttle !== null) StatusActionCreator.receiveThrottle(throttle);
      if (current_wp !== null) WaypointActionCreator.receiveCurrent(current_wp);
      if (mode !== null) StatusActionCreator.receiveCurrentMode(mode);
      if (wind !== null) StatusActionCreator.receiveWind(wind);
      if (gps !== null) StatusActionCreator.receiveGPS(gps);
      if (gps_status !== null && typeof gps_status !== 'number')
        StatusActionCreator.receiveGPSStatus(gps_status.satellite_number);
      if (signal !== null) StatusActionCreator.receiveSignalStrength(signal.signal_strength);
      if (safe !== null) StatusActionCreator.receiveSafetySwitch(safe);

      if (mav_info !== null && mav_info != _last_mav_info && mav_info != 'MAVProxy Error') {
        _last_mav_info = mav_info;
        alert.message(mav_info);
        CalibrationActionCreator.addCalibrationLine(mav_info);
      }
      if (mav_warning !== null && mav_warning != _last_mav_warning && mav_warning != 'MAVProxy Error') {
        _last_mav_warning = mav_warning;
        alert.message(mav_warning);
        CalibrationActionCreator.addCalibrationLine(mav_warning);
      }
      if (mav_error !== null && mav_error != _last_mav_error && mav_error != 'MAVProxy Error') {
        _last_mav_error = mav_error;
        alert.message(mav_error);
        CalibrationActionCreator.addCalibrationLine(mav_error);
      }
    }
  }).fail(() => {
    if (_mavproxy_up) alert.error('Lost connection to MAVProxy backend');
    _mavproxy_up = false;
    StatusActionCreator.disconnect();
  });
}

function getInteropData(time) {
  const data = time == undefined ? null : { tm: time };
  $.get({ url: api + 'interop', data }).done(data => {
    if (data !== 'Error: Server is not active' && validateData(data, interopValidate)) {
      const { obstacles, server_working, active_mission, mission_wp_dists } = JSON.parse(data);
      InteropActionCreator.receiveInteropActive(true);
      InteropActionCreator.receiveObstacles(obstacles);
      InteropActionCreator.receiveInteropAlive(server_working);
      InteropActionCreator.receiveMissionWpDists(mission_wp_dists);
      if (active_mission) {
        const { latitude, longitude } = active_mission.offAxisOdlcPos;
        InteropActionCreator.receiveOffAxis({ lat: latitude, lon: longitude });
      }
    } else {
      InteropActionCreator.receiveInteropActive(false);
    }
  });
}

function getSplines(time) {
  const data = time == undefined ? null : { tm: time };
  $.get({ url: api + 'wp/splines', data }).done(data => {
    if (validateData(data, splineValidate)) {
      const { splines } = JSON.parse(data);
      const changed_splines = splines.map(spline => ({
        start: spline[0],
        control1: spline[1],
        control2: spline[2],
        end: spline[3]
      }));
      WaypointActionCreator.receiveSplines(changed_splines);
    }
  });
}

function getPriorityRegions(time) {
  const data = time == undefined ? null : { tm: time };
  $.get({ url: api + 'distributed/regions', data: data }).done(data => {
    if (data !== 'Error: Server is not active' && validateData(data, regionValidate)) {
      const priorityRegions = JSON.parse(data).mdlc;
      const targets = JSON.parse(data).adlc;
      TargetImgActionCreator.receivePriorityRegions(priorityRegions);
      TargetImgActionCreator.receiveADLCTargets(targets);
    }
  });
}
//url: api + 'gimbal/roi'
//http://localhost:5001/ground/api/v3/gimbal/roi
function getRoi(time) {
  const data = time == undefined ? null : { tm: time };
  $.get({ url: api + 'gimbal/roi', data: data }).done(data => {
    //console.log(data);
    var dict = data;
    var re = dict.replace(/Infinity/g, 1);
    //console.log(re);

    //}
    const roi = JSON.parse(re);
    TargetImgActionCreator.receiveRoi(roi);
  });

}

function getPlaneInfo() {
  if (!_historical) {
    getStatusData();
    getWaypoints();

    //only updates this half of the time
    if (_non_urgent_update_counter === 0) getPlaneInfoNonUrgent();
    _non_urgent_update_counter = (_non_urgent_update_counter + 1) % _non_urgent_update_freq;
  }
}

/**
*this method gets called at half the refresh rate than the other methods since they
*are not as essential
*/
function getPlaneInfoNonUrgent() {
  getTargetImg();
  getParameters();
  getGimbalStatus();
  getCoverage();
  getPriorityRegions();
  getProgress();
  getSDA();
  getSplines();
  getAirdrop();
  getRoi();
}

function getInteropInfo() {
  if (!_historical) getInteropData();
}

/**
 * Gets the historical data for a given time
 * @param {number} time
 * @returns {undefined}
 */
export function getHistoricalData(time: number) {
  getStatusData(time);
  getInteropData(time);

  getParameters(time);
  getWaypoints(time);
  getSDA(time);

  getTargetImg(time);
  getGimbalStatus(time);
  getCoverage(time);
  getPriorityRegions(time);
  getRoi(time);
}

/**
 * Refreshes locations
 * @returns {undefined}
 */
export function getLocations() {
  $.get(api + 'getlocations').done(data => {
    SettingsActionCreator.receiveLocations(JSON.parse(data));
  });
}

/**
 * Initializes parameters list
 * @returns {undefined}
 */
export function initializeParameters() {
  $.get(api + 'params', data => {
    const params = JSON.parse(data);
    if ('FLTMODE1' in params) {
      StatusActionCreator.receiveModeSwitch(commandNumberTOword[params['FLTMODE1']]);
    }
    alert.success('Receiving Parameters');
    const paramsList = Object.keys(params).map(key => ({ name: key, value: params[key] }));
    ParametersActionCreator.receiveMultipleParameters(paramsList);
  });

  $.get(api + 'params/max', count => {
    ParametersActionCreator.receiveMaxParamCount(count);
  });
}

export function initializeCoverage() {
  $.ajax({
    url: api + 'coverage/search_grid',
    type: 'GET',
    contentType: 'application/json',
    dataType: 'json',
    success: data => {
      if (data != null) {
        const latlngs = data.map(pair => ({ lat: pair[0], lon: pair[1] }));
        TargetImgActionCreator.uploadCoverageFromFile(latlngs);
      }
    }
  });

  $.ajax({
    url: api + 'coverage',
    type: 'GET',
    contentType: 'application/json',
    dataType: 'json',
    success: data => {
      SettingsActionCreator.receiveExtensionDistance(data.extension_distance);
      SettingsActionCreator.receiveFlightHeight(data.flight_height);
      SettingsActionCreator.receiveCoverageGranularity(data.granularity);
      SettingsActionCreator.receiveMaxBank(data.max_bank);
      SettingsActionCreator.receiveMinCoverage(data.min_coverage);
    }
  });
}

/**
 * Initializes interop info
 * @returns {undefined}
 */
export function initializeInterop() {

  $.ajax({
    url: '/ground/api/v3/interop/setup',
    type: 'GET',
    contentType: 'application/json',
    success: (data) => {
      SettingsActionCreator.receiveInteropUrl(data.server_url);
      SettingsActionCreator.receiveInteropUsername(data.username);
      SettingsActionCreator.receiveInteropPassword(data.password);
      SettingsActionCreator.receiveInteropMissionID(data.mission_id);
    }
  });
}

/**
 * Starts plane receive loop
 * @param {number} timeout
 * @returns {undefined}
 */
export function startPlaneReceive(timeout: number) {
  initializeParameters();
  receiverProcess = setInterval(getPlaneInfo, timeout);
}

/**
 * Stops plane receive loop
 * @returns {undefined}
 */
export function stopPlaneReceive() {
  clearTimeout(receiverProcess);
}

/**
 * Starts interop receive loop
 * @param {number} timeout
 * @returns {undefined}
 */
export function startInteropReceive(timeout: number) {
  interopProcess = setInterval(getInteropInfo, timeout);
}

/**
 * Stops interop receive loop
 * @returns {undefined}
 */
export function stopInteropReceive() {
  clearTimeout(interopProcess);
}

/**
 * Halts current receive loop
 * @returns {undefined}
 */
export function haltReceiveLoop() {
  _historical = true;
}

/**
 * Resumes current receive loop
 * @returns {undefined}
 */
export function resumeReceiveLoop() {
  _historical = false;
}
