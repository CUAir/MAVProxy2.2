// @flow

import BabyParse from 'babyparse';

import * as WaypointActionCreator from 'js/actions/WaypointActionCreator';
import * as FenceActionCreator from 'js/actions/FenceActionCreator';
import * as ParametersActionCreator from 'js/actions/ParametersActionCreator';
import * as TargetActionCreator from 'js/actions/TargetImagesActionCreator';

import { sendGeofencePoints, sendCoverage } from 'js/utils/SendApi';

/**
 * @module utils/LoadApi
 */

/**
 * Loads waypoints from a file and sends them to the server
 * @param {Object} e
 * @returns {undefined}
 */
export function loadWaypointsFromFile(e: Object) {
  const file = e.target.files[0];
  const reader = new FileReader();

  reader.onload = () => {
    const lines = ('index\tcurrent\tframe\tcommand\tp1\tp2\tp3\tp4\tlon\tlat\talt\tautocontinue\n'
        + reader.result.replace(/\r\n/g, '\n')).split('\n');
    const text = lines.slice(0,1).concat(lines.slice(2)).join('\n');
    let waypoints = BabyParse.parse(text, {header: true, delimiter: '\t', comments: true, skipEmptyLines: true}).data;
    waypoints = waypoints.map(function(wp) {
      return {index: parseFloat(wp.index),
        current: parseFloat(wp.current),
        frame: parseFloat(wp.frame),
        command: parseFloat(wp.command),
        p1: parseFloat(wp.p1),
        p2: parseFloat(wp.p2),
        p3: parseFloat(wp.p3),
        p4: parseFloat(wp.p4),
        lon: parseFloat(wp.lon),
        lat: parseFloat(wp.lat),
        alt: parseFloat(wp.alt),
        autocontinue: parseFloat(wp.autocontinue)
      };
    });
    WaypointActionCreator.loadWaypointsFromFile(waypoints);
  };

  reader.readAsText(file);
}

/**
 * Loads parameters from a file and sends each to the server
 * @param {Object} e
 * @returns {undefined}
 */
export function loadParamsFromFile(e: Object) {
  const file = e.target.files[0];
  const reader = new FileReader();
  reader.onload = () => {
    const text = 'name,value\n' + reader.result.replace(/\r\n/g, '\n');
    const parseParams = {header: true, delimiter: ',', comments: true, skipEmptyLines: true};
    const parameters = BabyParse.parse(text, parseParams).data;
    ParametersActionCreator.loadParametersFromFile(parameters);
    ParametersActionCreator.receiveModalOpen(true);
  };

  reader.readAsText(file);
}

/**
 * Loads fences from a file and sends it to the server
 * @param {Object} e
 * @returns {undefined}
 */
export function loadFenceFromFile(e: Object) {
  const file = e.target.files[0];
  const reader = new FileReader();

  reader.onload = function() {
    const text = 'lat lon\n' + reader.result.replace(/\r\n/g, '\n');
    const parseParams = {header: true, delimiter: ' ', comments: true, skipEmptyLines: true};
    const points = BabyParse.parse(text, parseParams).data;
    sendGeofencePoints(points);
    FenceActionCreator.receiveFencePoints(points);
  };

  reader.readAsText(file);
}

export function loadCoverageFromFile(e: Object) {
  const file = e.target.files[0];
  const reader = new FileReader();

  reader.onload = function() {
    const text = 'lat lon\n' + reader.result.replace(/\r\n/g, '\n');
    const parseParams = {header: true, delimiter: ' ', comments: true, skipEmptyLines: true};
    const points = BabyParse.parse(text, parseParams).data;
    sendCoverage(points);
    TargetActionCreator.uploadCoverageFromFile(points);
  };

  reader.readAsText(file);
}
