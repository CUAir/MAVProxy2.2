// @flow

import BabyParse from 'babyparse';
import _ from 'lodash';

import { mToFt, time_to_start, time_to_minutes, time_to_date } from 'js/utils/ComponentUtils';
import type { PointType, FlightType, WaypointType, MiniWaypointType, ParamType, MiniParamType } from 'js/utils/Objects';

/**
 * @module utils/DownloadApi
 */

/**
 * Downloads a file using DOM magic
 * @param {string} text - string of text to be inserted into downloaded file
 * @param {string} filename - name of downloaded file
 * @returns {undefined}
 */
function download(text: string, filename: string): void {
  const element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);
  element.style.display = 'none';
  if (document.body != null) document.body.appendChild(element);
  element.click();
  if (document.body != null) document.body.removeChild(element);
}

/**
 * Generates a human-readable string of the current time and date
 * @returns {string} String of date (same as APM standard)
 */
function dateString(): string {
  const date = new Date();
  return `${(date.getMonth() + 1)}/${date.getDate()}/${date.getFullYear()} ` +
    `${('0' + date.getHours()).slice(-2)}:${('0' + date.getMinutes()).slice(-2)}:` +
    `${('0' + date.getSeconds()).slice(-2)}`;
}

/**
 * Generates a string of the current waypoint (for saving waypoints)
 * @param {number} current_wp - Index of the current waypoint in the sent list
 * @returns {function} Function that takes in a waypoint and index and
 * returns the stringified version of the waypoint according to QGC standards
 */
function waypointToString(current_wp: number): (WaypointType, number) => string {
  return function(wp, i) {
    const current = current_wp === i ? '1' : '0';
    return `${i}\t${current}\t0\t${wp.type}\t0\t0\t0\t0\t${wp.lon}\t${wp.lat}\t${wp.alt}\t1`;
  };
}

function minifyWaypoint(waypoint: WaypointType): MiniWaypointType {
  return {
    altitude_msl: waypoint.alt,
    latitude: waypoint.lat,
    longitude: waypoint.lon
  };
}

function isNavWaypoint(waypoint: WaypointType): boolean {
  return waypoint.type === 16;
}

function waypointsToMSL(waypoints: WaypointType[]): WaypointType[] {
  let waypoints_copy = _.cloneDeep(waypoints);
  const msl_height = waypoints_copy.length > 0 ? mToFt(waypoints_copy[0].alt) : 0;

  if (waypoints_copy.length > 0) waypoints_copy[0].alt = mToFt(waypoints_copy[0].alt);
  for (let i = 1; i < waypoints_copy.length; i++) {
    waypoints_copy[i].alt = mToFt(waypoints_copy[i].alt) + msl_height;
  }

  return waypoints_copy;
}

/**
 * Minifies a parameter down to its value and name (disregards other properties)
 * @param {FullParameter} param
 * @returns {Parameter} object containing value and name of given param
 */
function minifyParam(param: ParamType): ?MiniParamType {
  return typeof param.value !== 'number' ? null : {name: param.name, value: param.value};
}

/**
 * Saves waypoints to file in CSV format
 * @param {Waypoint[]} waypoints
 * @param {number} current
 * @returns {string}
 */
export function saveWaypointsToFile(waypoints: WaypointType[], current: number): string {
  const fixedWaypoints = waypoints.length > 0 ? waypoints.slice(0) : waypoints;
  const wps = fixedWaypoints.map(waypointToString(current)).join('\r\n');
  const file = 'QGC WPL 110\r\n' + wps;
  download(file, 'waypoints.wp');
  return file;
}

/**
 * Saves waypoints to file in JSON format
 * @param {Waypoint[]} waypoints
 * @returns {string}
 */
export function saveWaypointsToJson(waypoints: WaypointType[]): string {
  const fixedWaypoints = waypoints.length > 0 ? waypoints.slice(1) : waypoints;
  const wps = waypointsToMSL(fixedWaypoints).filter(isNavWaypoint).map(minifyWaypoint);
  const file = JSON.stringify(wps);
  download(file, 'waypoints_interop.wp');
  return file;
}

/**
 * Saves parameters to file
 * @param {string} note_input
 * @param {FullParameter[]} params
 * @returns {string}
 */
export function saveParamsToFile(note_input: string, params: ParamType[]): string {
  const miniParams = params.map(minifyParam).filter(param => param != null);
  const note = note_input === '' ? '' : ': ' + note_input;
  const csv = '#Note: ' + dateString() + note + '\r\n' + 
    BabyParse.unparse({fields: ['name', 'value'], data: miniParams});
  const lines = csv.split('\r\n');
  const file = lines.slice(0,1).concat(lines.slice(2)).join('\r\n');
  download(file, 'parameters.p');
  return file;
}

/**
 * Saves the fence points
 * @param {Point[]} fence_points
 * @returns {string}
 */
export function saveFenceToFile(fence_points: PointType[]): string {
  const geofence_height = 2000;
  const parsedPoints = fence_points.map(point => {
    return {lat: parseFloat(point.lat), lon: parseFloat(point.lon)};
  });
  const csv = '0 ' + geofence_height + 
    BabyParse.unparse({fields: ['lat', 'lon'], data: parsedPoints}, {delimiter: ' ', newline: '\n'});
  const file = csv.split('\n').slice(1).join('\n');
  download(file, 'fence.gf');
  return file;
}

export function downloadFlights(flights: FlightType[]): string {
  const header = 'date, airframe, start time, wind speed, wind direction, length, manual ' +
                 'time, 2-cell before, 6-cell before, 9-cell before, 2-cell after, ' +
                 '6-cell after, 9-cell after, waypoints, avg. min dist, flight notes\n';
  const csv = flights.map(flight => {
    return `${time_to_date(flight.date)},${flight.airframe},${time_to_start(flight.flightStart)},` +
           `${flight.windSpeed},${flight.windDirection},${time_to_minutes(flight.flightLength)},` +
           `${time_to_minutes(flight.manualTime)},${flight.batteryBefore.cell2}%,${flight.batteryBefore.cell6}%,` +
           `${flight.batteryBefore.cell9}%,${flight.batteryAfter.cell2}%,${flight.batteryAfter.cell6}%,` +
           `${flight.batteryAfter.cell9}%,${flight.waypointCount},${flight.avgDist},${flight.flightNotes}\n`;
  }).reduce((acc, cur) => acc + cur, '');
  const file_date = flights.length > 0 ? flights[flights.length - 1].date : (new Date()).getTime();
  download(header + csv, `flights-${time_to_date(file_date).replace('/', '-')}.csv`);
  return csv;
}
