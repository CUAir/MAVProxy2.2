// @flow

/**
 * @module utils/ComponentUtils
 */

import $ from 'jquery';
import { setScope } from 'js/utils/KeyBindings';

/**
 * Turns boolean into sweetalert class
 * @param {boolean} enabled
 * @returns {string}
 */
export function enabledToSuccess(enabled: boolean): string {
  return enabled ? 'green' : 'red';
}

/**
 * Turns color to button class
 * @param {string} color
 * @returns {string}
 */
export function colorToButton(color: string): string {
  if (color === 'success') return 'btn-success';
  else if (color === 'error') return 'btn-danger';
  else if (color === 'warning') return 'btn-warning';
  else return 'btn-primary';
}

/**
 * Alerts the user of some text
 * @param {string} message
 * @returns {string}
 */
export const alert = {
  // $FlowFixMe
  error: (m: string) => Materialize.toast(m, 2000, 'red lighten-2 toasty'), // eslint-disable-line no-undef
  // $FlowFixMe
  message: (m: string) => Materialize.toast(m, 2000, 'toasty'), // eslint-disable-line no-undef
  // $FlowFixMe
  success: (m: string) => Materialize.toast(m, 2000, 'green lighten-2 toasty'), // eslint-disable-line no-undef
  // $FlowFixMe
  warning: (m: string) => Materialize.toast(m, 2000, 'orange lighten-2 toasty') // eslint-disable-line no-undef
};


/**
 * Turns value to percent
 * @param {number} value
 * @returns {string}
 */
export function valueToPercent(value: number): string {
  return ': ' + parseInt(value) + '%';
}

/**
 * Turns percent into color
 * @param {number} value
 * @returns {string}
 */
export function valueToColor(value: number): string {
  if (value <= 30) return 'red lighten-2';
  else if (value <= 70) return 'orange lighten-2';
  else return 'green lighten-2';
}

/**
 * Turns percent into CSS color
 * @param {number} value
 * @returns {string}
 */
export function valueToColorName(value: number): string {
  if (value <= 30) return '#d9534f';
  else if (value <= 70) return '#f0ad4e';
  else return '#5cb85c';
}

/** 
 * Turns a date object to string
 * @param {Object} date
 * @returns {string}
 */
export function dateToString(date: Date): string {
  return `${date.getHours() % 12}:${('0' + date.getMinutes()).slice(-2)}:${('0' + date.getSeconds()).slice(-2)}`;
}

const sectionIds = ['home', 'settings', 'parameters', 'calibration', 'flightnotes', 'tuning-guide'];

/**
 * Creates a function to be called when a tab is clicked
 * @param {string} section
 * @returns {undefined}
 */
export function clickSection(section: string): void {
  sectionIds.forEach(id => {
    if (id === section) $(`#${id}`).show(); // eslint-disable-line no-undef
    else $(`#${id}`).hide(); // eslint-disable-line no-undef
  });

  setScope(section);
}

/**
 * Rounds [n] to [dec] decimal places
 * @param {number} n - the number to be rounded
 * @param {number} dec - the number of decimal places
 * @returns {number} Rounded number
 */
export function decround(n: number, dec: number): number {
  return Math.round(parseFloat(n) * Math.pow(10, dec)) / Math.pow(10, dec);
}

/**
 * Uses the pythagorean theorem to find scalar distance
 * @param {number} x
 * @param {number} y
 * @param {number} z
 * @returns {number} scalar
 */
export function pythagorean(x: number, y: number, z: number): number {
  return Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2) + Math.pow(z, 2));
}

const mInFt = 3.28084;
/**
 * Converts meters to feet
 * @param {number} meters
 * @returns {number}
 */
export function mToFt(meters: number): number {
  return meters * mInFt;
}

/**
 * Converts feet to meters
 * @param {number} feet
 * @returns {number}
 */
export function ftToM(feet: number): number {
  return feet / mInFt;
}

// for use in altitude unit calculations (prevent false redraws)
/**
 * Checks if n1 is close to n2:
 * @param {number} n1
 * @param {number} n2
 * @returns {boolean}
 */
export function valueClose(n1: number, n2: number): boolean {
  if (n1 === n2) return true;
  else if (n2 === 0) return Math.abs(n1) < 0.02;
  else return Math.abs((n2 - n1)/n2) < 0.005;
}

/**
 * Converts m/s to knots
 * @param {any} m_s
 * @returns {number}
 */
export function m_sToKnots(m_s: number | string): number {
  const m_s_num = parseFloat(m_s);
  return isNaN(m_s_num) ? 0 : 1.94384 * m_s_num;
}

/**
 * Converts radians to degrees
 * @param {any} m_s
 * @returns {number}
 */
export function rad_to_deg(radians: number): number {
  return radians * (180 / Math.PI);
}

/**
 * Converts a unix time to "start string"
 * @param {number} unix_time
 * @returns {string}
 */
export function time_to_start(unix_time: number): string {
  if (unix_time == 0) {
    return '0:0:0';
  } else {
    const date = new Date(unix_time);
    return `${('0' + (date.getHours() % 12)).slice(-2)}:${('0' + date.getMinutes()).slice(-2)}:${('0' + date.getSeconds()).slice(-2)}`;
  }
}

/**
 * Converts seconds to a valid time string
 * @param {number} total_seconds
 * @returns {string}
 */
export function time_to_minutes(total_seconds: number): string {
  const minutes = Math.floor(total_seconds / 60);
  const seconds = Math.floor(total_seconds % 60);
  return `${('0' + minutes).slice(-2)}:${('0' + seconds).slice(-2)}`;
}

/**
 * Converts a unix time to a date
 * @param {number} unix_time
 * @returns {string}
 */
export function time_to_date(unix_time: number): string {
  const datestr = (new Date(unix_time)).toISOString().slice(0,10).replace(/-/g,'');
  return `${datestr.slice(4, 6)}/${datestr.slice(6, 8)}/${datestr.slice(0, 4)}`;
}
