// @flow

import GlobalStore from 'js/stores/GlobalStore';

/**
 * @module actions/CalibrationActionCreator
 */

/**
 * Adds the given line to the calibration output
 * @param {string} line
 * @returns {undefined}
 */
export function addCalibrationLine(line: string): void {
  return GlobalStore.dispatch({
    type: 'ADD_CALIBRATION_LINE',
    line
  });
}

/**
 * Clears the calibration output
 * @returns {undefined}
 */
export function clearCalibrationLines(): void {
  return GlobalStore.dispatch({
    type: 'CLEAR_CALIBRATION'
  });
}
