// @flow

import GlobalStore from 'js/stores/GlobalStore';

import type { PlanePathPointType } from 'js/utils/Objects';

/**
 * @module actions/SdaActionCreator
 */



/**
 * Sets the obstacle list to the argument
 * @param {Obstacle[]} obstacles
 * @returns {undefined}
 */
export function receivePlanePreditions(plane_path: PlanePathPointType[]): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_PLANE_PATH',
    plane_path
  });
}




/**
 * Sets the sda enabled parameter to enabled or disabled
 * @param {boolean} enabled
 * @returns {undefined}
 */
export function receiveSdaEnabled(enabled: boolean): void {
  return GlobalStore.dispatch({
    type: 'RECEIVE_SDA_ENABLED',
    enabled
  });
}
