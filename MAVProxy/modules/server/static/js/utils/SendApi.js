// @flow

import $ from 'jquery';
import md5 from 'md5';

import { api } from 'js/constants/Sites';

import * as ParametersActionCreator from 'js/actions/ParametersActionCreator';
import * as WaypointActionCreator from 'js/actions/WaypointActionCreator';

import { tokenObj, confirmObj } from 'js/utils/ConfigData';
import type { MiniParamType, WaypointType, PointType } from 'js/utils/Objects';
import { alert } from 'js/utils/ComponentUtils';

/**
 * @module utils/SendApi
 */

const modeDict = {
  'MANUAL': 0, 'CIRCLE': 1, 'STABILIZE':2, 'TRAINING':3, 'ACRO': 4, 'FBWA': 5,
  'FBWB': 6, 'CRUISE': 7, 'AUTOTUNE': 8, 'AUTO': 10, 'RTL': 11, 'LOITER': 12, 'GUIDED' :15
};

function successGenerator(text: string, onSuccess = $.noop) {
  onSuccess = onSuccess == null ? $.noop : onSuccess;
  return data => {
    if (text) alert.success(text);
    onSuccess(data);
  };
}

function errorGenerator(text: string, onFail = $.noop) {
  onFail = onFail == undefined ? $.noop : onFail;
  return data => {
    if (text) alert.error(text);
    console.log(data); // eslint-disable-line no-console
    onFail(data);
  };
}

/**
 * Sends a parameter to the server
 * @param {Parameter} parameter - The parameter to be sent
 * @param {function} [onSuccess]
 * @param {function} [onFail]
 * @returns {undefined}
 */

export function sendParameter(parameter: MiniParamType, onSuccess: Function = $.noop, onFail: Function = $.noop) {
  onSuccess = onSuccess == null ? onSuccess : $.noop;
  onFail = onFail == null ? onFail : $.noop;

  function successfulChange(data) {
    alert.success(`${parameter.name} changed`);
    ParametersActionCreator.receiveSingleParameter(parameter.name, parameter.value);
    onSuccess(data);
  }

  function failedChange(data) {
    alert.error(`${parameter.name} failed to changed`);
    console.log(data); // eslint-disable-line no-console
    onFail(data);
  }

  alert.message(`Changing parameter ${parameter.name}`);
  $.ajax({
    url: api + 'params',
    type: 'POST',
    dataType: 'html',
    contentType: 'application/json',
    headers: tokenObj(),
    success: successfulChange,
    error: failedChange,
    data: JSON.stringify({pname: parameter.name, value: parseFloat(parameter.value)})
  });
}

/**
 * Sends all the parameters in the store to the server
 * @param {Parameter[]} parameters
 * @returns {undefined}
 */
export function sendAllParameters(parameters: MiniParamType[]) {
  parameters
    .filter(parameter => parameter.isTemp)
    .forEach(parameter => sendParameter(parameter));
}

/**
 * Send mode change to the server
 * @param {string} mode - The mode to be sent
 * @returns {undefined}
 */
export function sendChangeMode(mode: string) {
  $.ajax({
    url: api + 'set_mode',
    type: 'POST',
    dataType: 'html',
    contentType: 'application/json',
    headers: tokenObj(),
    success: successGenerator('Mode change succeeded'),
    error: errorGenerator('Mode change Failed'),
    data: JSON.stringify({mode: mode})
  });
}

/**
 * Send mode switch change to the server
 * @param {string} mode - The mode switch to be sent
 * @param {function} [onSuccess]
 * @param {function} [onFail]
 * @returns {undefined}
 */
export function sendModeSwitch(mode: string, onSuccess: Function = $.noop, onFail: Function = $.noop) {
  return sendParameter({name: 'FLTMODE1', value: modeDict[mode]}, onSuccess, onFail);
}

/**
 * Send an RTL mode change to the server
 * @returns {undefined}
 */
export function sendRTL() {
  return sendChangeMode('RTL');
}

/**
 * Sends a request to the server to delete a waypoint
 * @param {number} index - index of waypoint in list
 * @param {function} [onSuccess]
 * @param {function} [onFail]
 * @returns {undefined}
 */
export function deleteWP(index: number, onSuccess: Function = $.noop, onFail: Function = $.noop) {
  $.ajax({
    url: api + 'wp?wpnum=' + index,
    type: 'DELETE',
    contentType: 'application/json',
    headers: tokenObj(),
    success: successGenerator('Waypoint deleted', onSuccess),
    error: errorGenerator('Waypoint deletion failed', onFail)
  });
}

export function deleteAllWaypoints(onSuccess: Function = $.noop, onFail: Function = $.noop) {
  $.ajax({
    url: api + 'wp/clear_all',
    type: 'DELETE',
    contentType: 'application/json',
    headers: confirmObj(),
    success: successGenerator('Waypoints deleted', onSuccess),
    error: errorGenerator('Waypoints failed to delete', onFail)
  });
}

/**
 * Sends a request to the server to set a waypoint as current
 * @param {number} index - index of waypoint in list
 * @param {function} [onSuccess]
 * @param {function} [onFail]
 * @returns {undefined}
 */
export function setCurrentWP(index: number, onSuccess: Function = $.noop, onFail: Function = $.noop) {
  $.ajax({
    url: api + 'current',
    type: 'POST',
    contentType: 'application/json',
    headers: tokenObj(),
    success: successGenerator('Current waypoint changed', onSuccess),
    error: errorGenerator('Changing current waypoint failed', onFail),
    data: JSON.stringify({current: index})
  });
}

function waypointToServerWp(wp: WaypointType) {
  return {
    lat: wp.lat, sda: wp.isSda, lon: wp.lon, alt: wp.alt, index: wp.index, command: wp.type
  };
}

/**
 * Sends a request to the server to add a waypoint
 * @param {Waypoint} wp - waypoint to be added
 * @param {number} index - index of waypoint in list
 * @param {function} [onSuccess]
 * @param {function} [onFail]
 * @returns {undefined}
 */
export function sendWaypoint(wp: WaypointType, index: number, onSuccess: Function = $.noop, onFail: Function = $.noop) {
  $.ajax({
    url: api + 'wp',
    type: 'POST',
    contentType: 'application/json',
    headers: tokenObj(),
    success: successGenerator('Waypoint sent', onSuccess),
    error: errorGenerator('Waypoint failed to send', onFail),
    data: JSON.stringify(waypointToServerWp(wp))
  });
}

export function sendAllWaypoints(wps: WaypointType[], onSuccess: Function = $.noop, onFail: Function = $.noop) {
  $.ajax({
    url: api + 'wp',
    type: 'POST',
    contentType: 'application/json',
    headers: tokenObj(),
    success: successGenerator('Waypoints send', onSuccess),
    error: errorGenerator('Waypoints failed to send', onFail),
    data: JSON.stringify(wps.map(waypointToServerWp))
  });
}

export function sendAllSdaWaypoints(sdaWps: WaypointType[], onSuccess: Function = $.noop, onFail: Function = $.noop) {
  $.ajax({
    url: api + 'wp',
    type: 'POST',
    contentType: 'application/json',
    headers: tokenObj(),
    success: successGenerator('Waypoints send', onSuccess),
    error: errorGenerator('Waypoints failed to send', onFail),
    data: JSON.stringify(sdaWps.map(waypointToServerWp))
  });
}

/**
 * Sends a request to the server to add a list waypoint
 * @param {Waypoint[]} wpList - list waypoints to be added
 * @param {function} [onSuccess]
 * @param {function} [onFail]
 * @returns {undefined}
 */
export function sendWaypointList(wpList: WaypointType[], onSuccess: Function = $.noop, onFail: Function = $.noop) {
  $.ajax({
    url: api + 'wp/replace',
    type: 'DELETE',
    contentType: 'application/json',
    headers: confirmObj(),
    success: successGenerator('Waypoints sent', onSuccess),
    error: errorGenerator('Waypoints failed to send', onFail),
    data: JSON.stringify(wpList)
  });
}

/**
 * Sends a request to the server to update a waypoint
 * @param {Waypoint} wp - new values of waypoint
 * @param {number} index - index of waypoint in list
 * @param {function} [onSuccess]
 * @param {function} [onFail]
 * @returns {undefined}
 */
export function updateWP(wp: WaypointType, index: number, onSuccess: Function = $.noop, onFail: Function = $.noop) {
  $.ajax({
    url: api + 'wp',
    type: 'PUT',
    contentType: 'application/json',
    headers: tokenObj(),
    success: successGenerator('Waypoint updated', onSuccess),
    error: errorGenerator('Waypoint failed to update', onFail),
    data: JSON.stringify(waypointToServerWp(wp))
  });
}

/**
 * Sends a start sda request if the sda is off,
 * Sends a stop sda request if the sda is on
 * @param {boolean} enabled
 * @param {function} [onSuccess]
 * @param {function} [onFail]
 * @returns {undefined}
 */
export function toggleSda(enabled: boolean, onSuccess: Function = $.noop, onFail: Function = $.noop) {
  if (enabled) {
    $.ajax({
      type: 'DELETE',
      url: api + 'sda',
      contentType: 'application/json',
      headers: tokenObj(),
      success: successGenerator('SDA stopped', onSuccess),
      error: errorGenerator('SDA failed to stop', onFail)
    });
  } else {
    alert.message('Attempting to start SDA');
    $.ajax({
      type: 'POST',
      url: api + 'sda',
      contentType: 'application/json',
      headers: tokenObj(),
      success: successGenerator('SDA started', onSuccess),
      error: errorGenerator('SDA failed to start', onFail)
    });
  }
}

export function pointToOffAxis(enabled: boolean, offAxis: PointType, onSuccess: Function = $.noop, onFail: Function = $.noop) {
  if (offAxis.lat === 0) {
    alert.error('Interop gps not received');
  } else {
    const mode = !enabled ? 'off-axis' : 'fixed';
    const data = {'mode': mode,'lat': offAxis.lat,'lon': offAxis.lon};
    $.ajax({
      type: 'POST',
      url: api + 'distributed/camera/mode',
      contentType: 'application/json',
      data: JSON.stringify(data),
      datatype: 'json',
      success: successGenerator('Sent ' + mode +' mode to Platform', onSuccess),
      error: errorGenerator('Failed to send ' + mode +' mode to Platform', onFail)
    });
  }
}

export function pointToGimbal(enabled: boolean, gimbal_location: PointType, onSuccess: Function = $.noop, onFail: Function = $.noop) {
  if (!enabled) {
    if (gimbal_location.lat === 0) {
      alert.error('Gimbal location not set');
    } else {
      const gps = {'lat': gimbal_location.lat, 'lon': gimbal_location.lon};
      $.ajax({
        type: 'POST',
        url: api + 'distributed/gimbal',
        contentType: 'application/json',
        data: JSON.stringify(gps),
        datatype: 'json',
        success: successGenerator('Gimbal pointing to selected location', onSuccess),
        error: errorGenerator('Gimbal failed to point to selected location', onFail)
      });
    }
  } else {
    $.ajax({
      type: 'DELETE',
      url: api + 'distributed/gimbal',
      contentType: 'application/json',
      datatype: 'json',
      success: successGenerator('Gimbal switch to ground', onSuccess),
      error: errorGenerator('Gimbal failed to switch to ground', onFail)
    });
  }
}

/**
 * Sends a start accelerometer calibration request to the server
 * @returns {undefined}
 */
export function calibrationAStart() {
  $.ajax({
    type: 'POST',
    url: api + 'cali/accel',
    headers: tokenObj(),
    contentType: 'application/json',
    success: successGenerator('Acceleration calibration started'),
    error: errorGenerator('Acceleration calibration failed to start')
  });
}

/**
 * Sends a start gyroscope calibration request to the server
 * @returns {undefined}
 */
export function calibrationGStart() {
  $.ajax({
    type: 'POST',
    url: api + 'cali/gyro',
    headers: tokenObj(),
    contentType: 'application/json',
    success: successGenerator('Gyroscope calibration started'),
    error: errorGenerator('Gyroscope calibration failed to start')
  });
}

/**
 * Sends a start pressure calibration request to the server
 * @returns {undefined}
 */
export function calibrationPStart() {
  $.ajax({
    type: 'POST',
    url: api + 'cali/pressure',
    headers: tokenObj(),
    contentType: 'application/json',
    success: successGenerator('Pressure calibration started'),
    error: errorGenerator('Pressure calibration failed to start')
  });
}

/**
 * Sends a continue calibration request to the server
 * @returns {undefined}
 */
export function calibrationContinue() {
  $.ajax({
    type: 'PUT',
    headers: tokenObj(),
    contentType: 'application/json',
    url: api + 'cali/accel',
    success: successGenerator(''),
    error: errorGenerator('')
  });
}

/**
 * Sends a start RC calibration request to the server
 * @returns {undefined}
 */
export function calibrationRCStart() {
  $.ajax({
    type: 'POST',
    url: api + 'cali/rc',
    headers: tokenObj(),
    contentType: 'application/json',
    success: successGenerator('RC calibration started'),
    error: errorGenerator('RC calibration failed to start')
  });
}

/**
 * Sends a stop RC calibration request to the server
 * @returns {undefined}
 */
export function calibrationRCStop() {
  $.ajax({
    type: 'DELETE',
    url: api + 'cali/rc',
    headers: tokenObj(),
    contentType: 'application/json',
    success: successGenerator('RC calibration finished'),
    error: errorGenerator('RC calibration failed to finish')
  });
}

// Settings
/**
 * Sends geofence points to the server
 * @param {Point[]} points
 * @param {function} [onSuccess]
 * @param {function} [onFail]
 * @returns {undefined}
 */
export function sendGeofencePoints(points: PointType[], onSuccess: Function = $.noop, onFail: Function = $.noop) {
  $.ajax({
    type: 'POST',
    url: api + 'geofence',
    headers: tokenObj(),
    data: JSON.stringify(points),
    dataType: 'json',
    contentType: 'application/json',
    success: successGenerator('Geofence Points Sent', onSuccess),
    error: errorGenerator('Geofence Points Failed to Send', onFail)
  });
}

/**
 * Sends a start interop request if the interop is off,
 * Sends a stop interop request if the interop is on
 * @param {boolean} status
 * @param {function} [onSuccess]
 * @param {function} [onFail]
 * @returns {undefined}
 */
export function toggleInterop(status: boolean, server_url: string, username: string,
    password: string, mission_id: string, onSuccess: Function = $.noop, onFail: Function = $.noop) {
  const data = JSON.stringify({ server_url, username, password, mission_id});
  const headers = tokenObj();

  if (status) {
    alert.message('Attempting to stop interop');
    $.ajax({
      type: 'DELETE',
      url: api + 'interop',
      data,
      headers,
      contentType: 'application/json',
      success: successGenerator('Interop stopped', onSuccess),
      error: errorGenerator('Interop failed to stop', onFail)
    });
  } else {
    alert.message('Attempting to start interop');
    $.ajax({
      type: 'POST',
      url: api + 'interop',
      contentType: 'application/json',
      data,
      headers,
      success: successGenerator('Interop started', onSuccess),
      error: errorGenerator('Interop failed to start', onFail)
    });
  }
}

export function toggleDistributed(url: string, username: string, password: string,
    onSuccess: Function = $.noop, onFail: Function = $.noop) {
  const data = JSON.stringify({ url, username: 'Autopilot', password: md5(password) });
  const headers = tokenObj();

  alert.message('Attempting to connect to distributed');
  $.ajax({
    type: 'POST',
    url: api + 'distributed',
    contentType: 'application/json',
    data: data,
    headers: headers,
    success: successGenerator('Distributed connected', onSuccess),
    error: errorGenerator('Distributed failed to connect', onFail)
  });
}

/**
 * Toggles armed status
 * @param {boolean} armed
 * @returns {undefined}
 */
export function toggleArm(armed: boolean) {
  if (armed) {
    alert.message('Attempting to disarm');
    $.ajax({
      type: 'DELETE',
      url: api + 'arm',
      contentType: 'application/json',
      headers: confirmObj(),
      success: successGenerator('Disarm request sent!'),
      error: errorGenerator('Disarm request failed')
    });
  } else {
    alert.message('Attempting to arm');
    $.ajax({
      type: 'POST',
      url: api + 'arm',
      contentType: 'application/json',
      headers: confirmObj(),
      success: successGenerator('Arm Request Sent!'),
      error: errorGenerator('Arm request failed')
    });
  }
}

/**
 * Causes reboot
 * @returns {undefined}
 */
export function reboot() {
  $.ajax({
    type: 'POST',
    headers: confirmObj(),
    url: api + 'reboot',
    contentType: 'application/json',
    success: successGenerator('Reboot Request Sent!'),
    error: errorGenerator('Reboot Request Failed')
  });
}

/**
* Guides user through GUI to add Location and sends to backend.
* @returns {undefined}
*/
export function addLocation(locationdata: Object) {
  $.ajax({
    url:  api + 'cachemaps',
    type: 'POST',
    data: JSON.stringify(locationdata),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
    success: successGenerator('Success! Adding location.'),
    error: errorGenerator('Location add failed.')
  });
}

export function sendCoverage(coverage: PointType[]) {
  $.ajax({
    url: api + 'coverage/search_grid',
    type: 'POST',
    data: JSON.stringify(coverage),
    headers: tokenObj(),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
    success: successGenerator('Success! Sending Coverage Map.'),
    error: errorGenerator('Sending coverage failed.')
  });
}

export function requestCoveragePoints(settings: Object) {
  alert.message('Requesting Coverage Points');
  $.ajax({
    url: api + 'coverage',
    type: 'POST',
    data: JSON.stringify(settings),
    headers: tokenObj(),
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
    success: data => {
      alert.success('Received Coverage Points');
      WaypointActionCreator.receiveCoveragePoints(data);
    },
    error: data => {
      alert.error('Failed to Receive Coverage Points');
      console.log(data); // eslint-disable-line no-console
    }
  });
}

/**
 * Refreshes waypoint list on backend
 * @returns {undefined}
 */
export function refreshWPs() {
  $.ajax({
    type: 'PUT',
    headers: tokenObj(),
    url: api + 'wp/refresh',
    contentType: 'application/json',
    success: successGenerator('Successfully refreshed waypoints!'),
    error: errorGenerator('Failed to refresh waypoints')
  });
}

export function clearSplines() {
  $.ajax({
    url: api + 'wp/splines',
    type: 'DELETE',
    success: successGenerator('Cleared splines'),
    error: errorGenerator('Failed to clear splines')
  });
}

export function clearCoverage() {
  $.ajax({
    url: api + 'coverage',
    type: 'DELETE',
    success: successGenerator('Cleared coverage'),
    error: errorGenerator('Failed to clear coverage')
  });
}

export function simulateCoverage() {
  $.ajax({
    url: api + 'simcoverage',
    type: 'GET',
    success: successGenerator('Simulated Coverage'),
    error: errorGenerator('Failed to simulated coverage')
  });
}

/**
 * Sends the start and end waypoints for path planning between them
 * @returns {undefined}
 */
export function sendPointsForPathPlanning(points: PointType[], buf: Number, onSuccess: Function = $.noop, onFail: Function = $.noop) {
  const data = {'route_wp_indices': points, 'geofence': [], 'buffer': buf};
  $.ajax({
    type: 'POST',
    url: api + 'path_planning',
    headers: tokenObj(),
    data: JSON.stringify(data),
    dataType: 'json',
    contentType: 'application/json',
    success: successGenerator('Start and End Waypoints Sent', onSuccess),
    error: errorGenerator('Start and End Waypoints Failed to Send', onFail)
  });
}

/**
 * Delete all the sda waypoints
 * @returns {undefined}
 */
export function deleteSdaWps(onSuccess: Function = $.noop, onFail: Function = $.noop) {
  $.ajax({
    type: 'DELETE',
    url: api + 'path_planning/delete',
    success: successGenerator('Deleted SDA WPs', onSuccess),
    error: errorGenerator('Failed to delete SDA WPs', onFail)
  });
}

